import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth_module.db.cruds.account_crud import AccountCRUD
from app.modules.auth_module.dependencies.jwt_decode import authenticate_websocket_user
from app.modules.base_module.services.base_service import BaseService
from app.modules.chat_module.websoket.connection_manager import connetion_manager

if TYPE_CHECKING:
    from app.modules.auth_module.schemas.account import AccountDBSchema


class WebsocketService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.manager = connetion_manager
        self.account_crud = AccountCRUD(session)

    async def handle_incoming_connection(self, websocket: WebSocket, chat_id: UUID):
        await websocket.accept()
        auth_message = await websocket.receive_text()
        account_schema = await self.authorize_account(auth_message)
        if not account_schema:
            await websocket.send_text(
                json.dumps({"type": "auth_error", "message": "Authentication failed"})
            )
            await websocket.close(code=1008, reason="Authentication failed")
            return

        profile_id = account_schema.profile.id
        await self.manager.connect(websocket, profile_id)

        try:
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                logging.info(f"Received message: {message_data}")
                await self.handle_websocket_message(message_data, profile_id, websocket)

        except WebSocketDisconnect:
            self.manager.disconnect(websocket, profile_id)

    async def authorize_account(self, auth_message: str) -> "AccountDBSchema | bool":
        authenticated_user = None
        try:
            auth_data = json.loads(auth_message)
            if auth_data.get("type") == "auth":
                token = auth_data.get("token", "")
                authenticated_user = await authenticate_websocket_user(token)

                if authenticated_user:
                    account_db: "AccountDBSchema" = await self.account_crud.get_by_id(
                        authenticated_user.id
                    )
                    return account_db

        except json.JSONDecodeError:
            logging.warning(f"Invalid auth message: {auth_message}")
            return False

        return False

    async def handle_websocket_message(
        self,
        message_data: dict,
        user_id: UUID,
        websocket: WebSocket,
    ):
        """
        Обработчик входящих WebSocket сообщений

        Args:
            message_data: Данные сообщения
            user_id: ID пользователя
            websocket: WebSocket соединение
        """
        try:
            message_type = message_data.get("type")

            if message_type == "join_chat":
                await self.handle_join_chat(message_data, user_id, websocket)

            elif message_type == "leave_chat":
                await self.handle_leave_chat(message_data, user_id, websocket)

            elif message_type == "send_message":
                await self.handle_send_message(message_data, user_id)

            elif message_type == "mark_read":
                await self.handle_mark_read(message_data, user_id)

            elif message_type == "typing":
                await self.handle_typing(message_data, user_id)

            else:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )

        except Exception as e:
            logging.error(f"Error handling websocket message: {e}")
            await websocket.send_text(
                json.dumps(
                    {"type": "error", "message": f"Failed to process message: {e}"}
                )
            )

    async def handle_join_chat(
        self,
        message_data: dict,
        user_id: UUID,
        websocket: WebSocket,
    ):
        """Обработка присоединения к чату"""
        chat_id = UUID(message_data.get("chat_id"))
        try:
            # FIXME: Добавить возможность получить информацию о чате

            await self.manager.join_chat(user_id, chat_id)
            await self.manager.send_chat_message(
                {
                    "type": "user_joined",
                    "chat_id": str(chat_id),
                    "user_id": str(user_id),
                    "timestamp": str(datetime.utcnow()),
                },
                chat_id,
                exclude_user=user_id,
            )

            await websocket.send_text(
                json.dumps(
                    {
                        "type": "joined_chat",
                        "chat_id": str(chat_id),
                    }
                )
            )

        except ValueError:
            await websocket.send_text(
                json.dumps(
                    {"type": "error", "message": "You are not a member of this chat"}
                )
            )

    async def handle_leave_chat(
        self, message_data: dict, user_id: UUID, websocket: WebSocket
    ):
        """Обработка покидания чата"""
        chat_id = UUID(message_data.get("chat_id"))

        await self.manager.leave_chat(user_id, chat_id)
        await self.manager.send_chat_message(
            {
                "type": "user_left",
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "timestamp": str(datetime.utcnow()),
            },
            chat_id,
            exclude_user=user_id,
        )

    async def handle_send_message(
        self,
        message_data: dict,
        user_id: UUID,
    ):
        """Обработка отправки сообщения"""
        # TODO: Сделать сохранение сообщений в БД
        chat_id = UUID(message_data.get("chat_id"))
        text = message_data.get("text")

        # Сохраняем сообщение в БД
        # message = await message_service.create_message(
        #     {"chat_id": chat_id, "sender_id": user_id, "text": text}
        # )
        # await session.commit()

        # Отправляем всем участникам чата
        await self.manager.broadcast_to_chat(
            {
                "type": "new_message",
                "message": {
                    # "id": str(message.id),
                    # "chat_id": str(message.chat_id),
                    # "sender_id": str(message.sender_id),
                    # "text": message.text,
                    # "sent_at": message.sent_at.isoformat() if message.sent_at else None,
                    # "read_at": message.read_at.isoformat() if message.read_at else None,
                    "id": str(uuid4()),
                    "chat_id": str(chat_id),
                    "sender_id": str(user_id),
                    "text": text,
                    "sent_at": str(datetime.utcnow()),
                    "read_at": None,
                },
            },
            chat_id,
        )

    async def handle_mark_read(
        self,
        message_data: dict,
        user_id: UUID,
        session: AsyncSession,
    ):
        """Обработка отметки о прочтении"""
        message_id = UUID(message_data.get("message_id"))

        # Отмечаем сообщение как прочитанное
        await message_service.mark_message_read(message_id, user_id)
        await session.commit()

        # Уведомляем отправителя
        message_info = await message_service.get_message(message_id)
        await self.manager.send_personal_message(
            {
                "type": "message_read",
                "message_id": str(message_id),
                "read_by": str(user_id),
                "timestamp": str(datetime.utcnow()),
            },
            message_info.sender_id,
        )

    async def handle_typing(self, message_data: dict, user_id: UUID):
        """Обработка индикатора печати"""
        chat_id = UUID(message_data.get("chat_id"))
        is_typing = message_data.get("is_typing", False)

        # Уведомляем других участников о печати
        await self.manager.send_chat_message(
            {
                "type": "typing",
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "is_typing": is_typing,
            },
            chat_id,
            exclude_user=user_id,
        )
