import json
import logging
from collections import defaultdict
from typing import Dict, List
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """Менеджер WebSocket соединений"""

    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = defaultdict(list)
        self.chat_connections: Dict[UUID, Dict[UUID, List[WebSocket]]] = defaultdict(
            lambda: defaultdict(list)
        )

    async def connect(self, socket: WebSocket, user_id: UUID):
        """Подключение пользователя"""
        self.active_connections[user_id].append(socket)
        logging.info(
            f"Account.ID {user_id} connected. Total connections: {len(self.active_connections[user_id])}"
        )

    def profile_is_in_chat(self, chat_id: UUID, profile_id: UUID) -> bool:
        """Проверить, находится ли пользователь в чате (хотя бы с одного устройства)"""
        chat_connections = self.chat_connections.get(chat_id, {}).get(profile_id, [])
        return len(chat_connections) > 0

    def profile_has_multiple_devices_in_chat(
        self, chat_id: UUID, profile_id: UUID
    ) -> bool:
        """Проверить, есть ли у пользователя несколько устройств в чате"""
        chat_connections = self.chat_connections.get(chat_id, {}).get(profile_id, [])
        return len(chat_connections) > 1

    def disconnect(self, socket: WebSocket, user_id: UUID):
        """Отключение пользователя"""
        # Удаляем из активных соединений
        if user_id in self.active_connections:
            if socket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(socket)

            # Если у пользователя не осталось активных соединений
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Удаляем из всех чатов
        for chat_id in list(self.chat_connections.keys()):
            if user_id in self.chat_connections[chat_id]:
                if socket in self.chat_connections[chat_id][user_id]:
                    self.chat_connections[chat_id][user_id].remove(socket)

                # Если у пользователя не осталось соединений в чате
                if not self.chat_connections[chat_id][user_id]:
                    del self.chat_connections[chat_id][user_id]

                    # Если в чате не осталось пользователей, удаляем чат
                    if not self.chat_connections[chat_id]:
                        del self.chat_connections[chat_id]

        logging.info(f"Account.ID {user_id} disconnected")

    async def join_chat(self, user_id: UUID, chat_id: UUID):
        """Присоединение пользователя к чату"""
        if user_id in self.active_connections:
            for socket in self.active_connections[user_id]:
                if socket not in self.chat_connections[chat_id][user_id]:
                    self.chat_connections[chat_id][user_id].append(socket)

        logging.info(f"User {user_id} joined chat {chat_id}")

    async def leave_chat(self, user_id: UUID, chat_id: UUID):
        """Покидание чата - удаляет ВСЕ устройства пользователя из чата"""
        if (
            chat_id in self.chat_connections
            and user_id in self.chat_connections[chat_id]
        ):
            del self.chat_connections[chat_id][user_id]
            logging.info(f"User {user_id} left chat {chat_id}")

    async def leave_chat_single_device(
        self, user_id: UUID, chat_id: UUID, socket: WebSocket
    ):
        """Покидание чата конкретным устройством"""
        if (
            chat_id in self.chat_connections
            and user_id in self.chat_connections[chat_id]
        ):
            if socket in self.chat_connections[chat_id][user_id]:
                self.chat_connections[chat_id][user_id].remove(socket)

                # Если у пользователя не осталось соединений в чате
                if not self.chat_connections[chat_id][user_id]:
                    del self.chat_connections[chat_id][user_id]

        logging.info(f"User {user_id} left chat {chat_id} from one device")

    async def send_personal_message(self, message: dict, user_id: UUID):
        """Отправка личного сообщения пользователю"""
        if user_id in self.active_connections:
            disconnected_sockets = []
            for socket in self.active_connections[user_id].copy():
                try:
                    await self.send_message_to_socket(socket, message)
                except Exception as e:
                    logging.error(f"Error sending message to user {user_id}: {e}")
                    disconnected_sockets.append(socket)

            for socket in disconnected_sockets:
                self.disconnect(socket, user_id)

    async def send_chat_message(
        self, message: dict, chat_id: UUID, exclude_user: UUID = None
    ):
        """Отправка сообщения всем участникам чата"""
        if chat_id not in self.chat_connections:
            return
        disconnected_sockets = []
        for user_id, sockets in self.chat_connections[chat_id].copy().items():
            # Исключаем отправителя, если нужно
            if exclude_user and user_id == exclude_user:
                continue

            for socket in sockets.copy():
                try:
                    await self.send_message_to_socket(socket, message)
                except Exception as e:
                    logging.error(
                        f"Error sending message to user {user_id} in chat {chat_id}: {e}"
                    )
                    disconnected_sockets.append((socket, user_id))

        for socket, user_id in disconnected_sockets:
            self.disconnect(socket, user_id)

    async def broadcast_to_chat(self, message: dict, chat_id: UUID):
        """Рассылка сообщения всем участникам чата включая отправителя"""
        await self.send_chat_message(message, chat_id)

    def get_chat_online_users(self, chat_id: UUID) -> List[UUID]:
        """Получить список онлайн пользователей в чате"""
        if chat_id in self.chat_connections:
            return list(self.chat_connections[chat_id].keys())
        return []

    def get_chat_stats(self, chat_id: UUID) -> dict:
        """Получить статистику чата"""
        if chat_id not in self.chat_connections:
            return {"users": 0, "connections": 0, "users_with_multiple_devices": 0}

        users = len(self.chat_connections[chat_id])
        total_connections = sum(
            len(sockets) for sockets in self.chat_connections[chat_id].values()
        )
        users_with_multiple_devices = sum(
            1 for sockets in self.chat_connections[chat_id].values() if len(sockets) > 1
        )

        return {
            "users": users,
            "connections": total_connections,
            "users_with_multiple_devices": users_with_multiple_devices,
        }

    def is_user_online(self, user_id: UUID) -> bool:
        """Проверить, онлайн ли пользователь"""
        return (
            user_id in self.active_connections
            and len(self.active_connections[user_id]) > 0
        )

    def get_user_connection_count(self, user_id: UUID) -> int:
        """Получить количество активных соединений пользователя"""
        return len(self.active_connections.get(user_id, []))

    async def user_authorized(
        self, socket: WebSocket, profile_id: UUID, chat_id: UUID
    ) -> None:
        await self.send_message_to_socket(
            socket,
            {
                "type": "auth_success",
                "user_id": str(profile_id),
                "chat_id": str(chat_id),
            },
        )

    async def close_chat_not_found(self, socket: WebSocket):
        await self.send_message_to_socket(
            socket, {"type": "auth_error", "message": "Chat not found"}
        )
        await self._close_socket(socket, 1008, "Chat not found")

    async def close_as_not_a_member(self, socket: WebSocket):
        await self.send_message_to_socket(
            socket,
            {"type": "auth_error", "message": "You are not a member of this chat"},
        )
        await self.close_access_denied(socket)

    async def close_as_unauthorized(self, socket: WebSocket):
        message = {"type": "auth_error", "message": "Authentication failed"}
        await self.send_message_to_socket(socket, message)
        await self._close_socket(socket, 1008, "Authentication failed")

    async def close_access_denied(self, socket: WebSocket):
        await self._close_socket(socket, 1008, "Access denied")

    async def close_as_internal_error(self, socket: WebSocket):
        if socket.client_state != 3:  # WebSocketState.DISCONNECTED
            await self._close_socket(socket, code=1011, reason="Internal server error")

    async def _close_socket(self, socket: WebSocket, code: int, reason: str) -> None:
        await socket.close(code=code, reason=reason)

    async def send_message_to_socket(self, socket: WebSocket, message: dict):
        await socket.send_text(json.dumps(message))

    async def receive_message_from_socket(self, socket: WebSocket) -> dict:
        message = await socket.receive_text()
        return json.loads(message)


connection_manager = ConnectionManager()
