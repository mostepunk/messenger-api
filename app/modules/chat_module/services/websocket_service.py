import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth_module.dependencies.jwt_decode import authenticate_websocket_user
from app.modules.base_module.db.errors import ItemNotFoundError
from app.modules.base_module.services.base_service import BaseService
from app.modules.chat_module.db.cruds.chat_crud import ChatCRUD
from app.modules.chat_module.db.cruds.message_crud import MessageCRUD
from app.modules.chat_module.db.cruds.profile_crud import ProfileCRUD
from app.modules.chat_module.services.deduplication_service import deduplication_service
from app.modules.chat_module.websoket.connection_manager import connection_manager
from app.settings import config
from app.settings.base import ApiMode

if TYPE_CHECKING:
    from app.modules.chat_module.schemas.chat_schemas import ChatDBSchema
    from app.modules.chat_module.schemas.message_schema import MessageDBSchema
    from app.modules.chat_module.schemas.profile_schemas import ProfileDBSchema


class WebsocketService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.manager = connection_manager
        self.profile_crud = ProfileCRUD(session)
        self.message_crud = MessageCRUD(session)
        self.chat_crud = ChatCRUD(session)
        self.dedup_service = deduplication_service

    async def handle_incoming_connection(self, websocket: WebSocket, chat_id: UUID):
        await websocket.accept()
        profile_id = None

        try:
            auth_message = await websocket.receive_text()
            profile_schema = await self.authorize_account(auth_message)

            if not profile_schema:
                logging.info(f"Profile.ID {profile_schema} authorized")
                await self.manager.close_as_unauthorized(websocket)
                return

            profile_id = profile_schema.id
            await self.manager.connect(websocket, profile_id)
            await self.manager.user_authorized(websocket, profile_id, chat_id)

            is_joined = await self.auto_join_chat(chat_id, profile_id, websocket)
            if not is_joined:
                await self.manager.disconnect(websocket, profile_id)
                return
            await self.send_chat_history(chat_id, profile_id, websocket)

            while True:
                message_data = await self.manager.receive_message_from_socket(websocket)
                if config.environment in (ApiMode.dev, ApiMode.local):
                    logging.debug(
                        f"Profile.ID {profile_id} Received message: {message_data}"
                    )
                else:
                    logging.debug(
                        f"Profile.ID {profile_id} Received message type: {message_data.get('type', 'unknown')}"
                    )
                await self.handle_websocket_message(
                    message_data, profile_id, websocket, chat_id
                )

        except WebSocketDisconnect:
            logging.info(
                f"WebSocket disconnected for Profile.ID {profile_id if 'profile_id' in locals() else 'unknown'}"
            )
            if "profile_id" in locals() and "chat_id" in locals():
                await self.handle_disconnect(profile_id, chat_id)
                await self.manager.disconnect(websocket, profile_id)

        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            await self.manager.close_as_internal_error(websocket)

    async def authorize_account(self, auth_message: str) -> "ProfileDBSchema| None":
        try:
            auth_data = json.loads(auth_message)
            if auth_data.get("type") == "auth":
                token = auth_data.get("token", "")
                authenticated_user = await authenticate_websocket_user(token)

                if authenticated_user:
                    profile_db: "ProfileDBSchema" = (
                        await self.profile_crud.get_profile_by_account_id(
                            authenticated_user.id
                        )
                    )
                    return profile_db

        except json.JSONDecodeError:
            logging.warning("Invalid auth message format")
        except Exception as e:
            logging.error(f"Authorization error: {e}")

        return None

    async def auto_join_chat(
        self, chat_id: UUID, profile_id: UUID, websocket: WebSocket
    ) -> bool:
        """Автоматическое присоединение к чату после аутентификации"""
        try:
            db_chat: "ChatDBSchema" = await self.chat_crud.get_by_id(chat_id)
            members_ids: list[UUID] = [member.id for member in db_chat.members]

            if profile_id not in members_ids:
                await self.manager.close_as_not_a_member(websocket)
                return False

            await self.manager.join_chat(profile_id, chat_id)
            # не посылать уведомление, что пользователь вошел в чат, если он зашел с другого устройства
            if await self.manager.profile_has_multiple_devices_in_chat(
                chat_id, profile_id
            ):
                logging.debug(
                    f"Profile.ID {profile_id} connected from additional device to chat {chat_id}"
                )
                return True

            await self.manager.send_chat_message(
                {
                    "type": "user_joined",
                    "chat_id": str(chat_id),
                    "user_id": str(profile_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                chat_id,
                exclude_user=profile_id,
            )
            return True

        except ItemNotFoundError:
            logging.warning(f"Chat.ID {chat_id} Not Found")
            await self.manager.close_chat_not_found(websocket)
            return False

    async def send_chat_history(
        self, chat_id: UUID, profile_id: UUID, websocket: WebSocket, limit: int = 10
    ):
        """Отправка истории сообщений"""
        try:
            # total_count: int, messages: list[MessageDBSchema]
            total_count, messages = await self.message_crud.chat_history(
                chat_id, limit=limit, offset=0
            )
            message = {
                "type": "chat_history",
                "messages": [message.model_dump(mode="json") for message in messages],
                "total_count": total_count,
                "unread_count": 0,
            }
            await self.manager.send_message_to_socket(websocket, message)
            logging.debug(f"Sent chat history for user {profile_id}")

        except Exception as err:
            logging.error(f"Error sending chat history: {err}")
            message = {"type": "error", "message": "Failed to load chat history"}
            await self.manager.send_message_to_socket(websocket, message)

    async def handle_websocket_message(
        self,
        message_data: dict,
        user_id: UUID,
        websocket: WebSocket,
        chat_id: UUID,
    ):
        """Обработчик входящих WebSocket сообщений"""
        try:
            message_type = message_data.get("type")

            if message_type == "send_message":
                await self.handle_send_message(message_data, user_id, chat_id)

            elif message_type == "leave_chat":
                await self.handle_leave_chat(message_data, user_id, chat_id)

            elif message_type == "mark_read":
                await self.handle_mark_read(message_data, user_id, chat_id)

            elif message_type == "mark_single_read":
                await self.handle_mark_single_read(message_data, user_id)

            elif message_type == "typing":
                await self.handle_typing(message_data, user_id, chat_id)

            elif message_type == "get_chat_history":
                await self.handle_get_chat_history(
                    message_data, user_id, websocket, chat_id
                )

            elif message_type == "get_unread_count":
                await self.handle_get_unread_count(user_id, websocket, chat_id)

            else:
                await self.manager.send_message_to_socket(
                    websocket,
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                )

        except Exception as e:
            logging.error(f"Error handling websocket message: {e}")
            await self.manager.send_message_to_socket(
                websocket,
                {"type": "error", "message": f"Failed to process message: {str(e)}"},
            )

    async def handle_leave_chat(
        self, message_data: dict, profile_id: UUID, chat_id: UUID
    ):
        """Обработка покидания чата"""
        try:
            await self.manager.leave_chat(profile_id, chat_id)
            if not await self.manager.profile_is_in_chat(chat_id, profile_id):
                await self.manager.send_chat_message(
                    {
                        "type": "user_left",
                        "chat_id": str(chat_id),
                        "user_id": str(profile_id),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    chat_id,
                    exclude_user=profile_id,
                )
                logging.info(f"User {profile_id} completely left chat {chat_id}")
            else:
                logging.info(
                    f"User {profile_id} disconnected one device from chat {chat_id}"
                )

        except Exception as err:
            logging.error(f"Error Profile.ID {profile_id} leave chat: {err}")

    async def handle_disconnect(self, user_id: UUID, chat_id: UUID):
        """Обработка отключения пользователя (вызывается при WebSocketDisconnect)"""
        try:
            await self.manager.send_chat_message(
                {
                    "type": "user_disconnected",
                    "chat_id": str(chat_id),
                    "user_id": str(user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                chat_id,
                exclude_user=user_id,
            )

            logging.info(f"User {user_id} disconnected from chat {chat_id}")

        except Exception as e:
            logging.error(f"Error handling disconnect: {e}")

    async def handle_send_message(
        self, message_data: dict, user_id: UUID, chat_id: UUID
    ):
        """Обработка отправки сообщения"""
        text = message_data.get("text")
        if not text or not text.strip():
            return
        try:
            is_allowed, reason = await self.dedup_service.check_and_prevent_duplicate(
                user_id, chat_id, text
            )
            if not is_allowed:
                await self.manager.send_personal_message(
                    {"type": "error", "message": f"Message blocked: {reason}"}, user_id
                )
                logging.info(f"Blocked duplicate message from user {user_id}: {reason}")
                return

            message: "MessageDBSchema" = await self.message_crud.add(
                {
                    "chat_id": chat_id,
                    "sender_id": user_id,
                    "text": text.strip(),
                    "sent_at": datetime.utcnow(),
                }
            )
            await self.session.commit()
            await self.manager.broadcast_to_chat(
                {"type": "new_message", "message": message.model_dump(mode="json")},
                chat_id,
            )
            await self.dedup_service.mark_message_sent(reason, message.id)

        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await self.manager.send_personal_message(
                {"type": "error", "message": "Failed to send message"}, user_id
            )

    async def handle_mark_read(
        self, message_data: dict, profile_id: UUID, chat_id: UUID
    ):
        """Обработка отметки сообщений как прочитанных до определенного ID"""
        last_read_message_id = message_data.get("last_read_message_id")
        if not last_read_message_id:
            return

        try:
            newly_read_message_ids = (
                await self.message_crud.mark_messages_read_by_last_id(
                    chat_id, profile_id, last_read_message_id
                )
            )
            await self.session.commit()

            if newly_read_message_ids:
                # Получаем детальную информацию о прочитанных сообщениях для уведомления
                read_messages_info = await self.message_crud.get_messages_by_ids(
                    newly_read_message_ids
                )
                await self.manager.broadcast_to_chat(
                    {
                        "type": "messages_read",
                        "chat_id": str(chat_id),
                        "read_by": str(profile_id),
                        "message_ids": [
                            str(msg_id) for msg_id in newly_read_message_ids
                        ],
                        "read_count": len(newly_read_message_ids),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    chat_id,
                )
                # Уведомляем отправителей прочитанных сообщений персонально
                senders = set()
                for msg_info in read_messages_info:
                    if msg_info.sender_id and msg_info.sender_id != profile_id:
                        senders.add(msg_info.sender_id)

                for sender_id in senders:
                    await self.manager.send_personal_message(
                        {
                            "type": "your_messages_read",
                            "chat_id": str(chat_id),
                            "read_by": str(profile_id),
                            "read_count": len(newly_read_message_ids),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        sender_id,
                    )

        except Exception as e:
            logging.error(f"Error marking messages as read: {e}")

    async def handle_mark_single_read(self, message_data: dict, profile_id: UUID):
        """Обработка отметки одного сообщения как прочитанного"""
        message_id = message_data.get("message_id")

        if not message_id:
            return

        try:
            message_uuid = UUID(message_id)
            was_marked = await self.message_crud.mark_as_read_by_profile(
                message_uuid, profile_id
            )
            message_db = await self.message_crud.get_by_id(message_uuid)

            await self.manager.send_personal_message(
                {
                    "type": "message_read",
                    "message_id": str(message_uuid),
                    "read_by": str(profile_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                message_db.sender.id,
            )

        except Exception as e:
            logging.error(f"Error marking single message as read: {e}")

    async def handle_typing(self, message_data: dict, user_id: UUID, chat_id: UUID):
        """Обработка индикатора печати"""
        is_typing = message_data.get("is_typing", False)

        try:
            await self.manager.send_chat_message(
                {
                    "type": "typing",
                    "chat_id": str(chat_id),
                    "user_id": str(user_id),
                    "is_typing": is_typing,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                chat_id,
                exclude_user=user_id,
            )
        except Exception as e:
            logging.error(f"Error handling typing indicator: {e}")

    async def handle_get_chat_history(
        self, message_data: dict, user_id: UUID, websocket: WebSocket, chat_id: UUID
    ):
        """Обработка запроса истории чата"""
        limit = message_data.get("limit", 10)
        offset = message_data.get("offset", 0)

        await self.send_chat_history(chat_id, user_id, websocket, limit)

    async def handle_get_unread_count(
        self, profile_id: UUID, websocket: WebSocket, chat_id: UUID
    ):
        """Обработка запроса количества непрочитанных сообщений"""
        try:
            unread_count = await self.message_crud.get_unread_count_for_user(
                chat_id, profile_id
            )
            await self.manager.send_message_to_socket(
                websocket,
                {
                    "type": "unread_count",
                    "chat_id": str(chat_id),
                    "count": unread_count,
                },
            )
        except Exception as e:
            logging.error(f"Error getting unread count: {e}")
            await self.manager.send_message_to_socket(
                websocket,
                {"type": "error", "message": "Failed to get unread count"},
            )
