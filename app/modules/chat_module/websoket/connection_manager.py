import json
import logging
from typing import Dict, List
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """Менеджер WebSocket соединений"""

    def __init__(self):
        # Активные соединения: {user_id: [websockets]}
        self.active_connections: Dict[UUID, List[WebSocket]] = {}
        # Соединения по чатам: {chat_id: {user_id: [websockets]}}
        self.chat_connections: Dict[UUID, Dict[UUID, List[WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        """Подключение пользователя"""
        # TODO: переделать на defaultdict
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logging.info(
            f"Account.ID {user_id} connected. Total connections: {len(self.active_connections[user_id])}"
        )

    def disconnect(self, websocket: WebSocket, user_id: UUID):
        """Отключение пользователя"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            # Удаляем из всех чатов
            for chat_id in self.chat_connections:
                if user_id in self.chat_connections[chat_id]:
                    if websocket in self.chat_connections[chat_id][user_id]:
                        self.chat_connections[chat_id][user_id].remove(websocket)

                    # Если у пользователя не осталось соединений в чате
                    if not self.chat_connections[chat_id][user_id]:
                        del self.chat_connections[chat_id][user_id]

            # Если у пользователя не осталось активных соединений
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logging.info(f"Account.ID {user_id} disconnected")

    async def join_chat(self, user_id: UUID, chat_id: UUID):
        """Присоединение пользователя к чату"""
        if chat_id not in self.chat_connections:
            self.chat_connections[chat_id] = {}

        if user_id not in self.chat_connections[chat_id]:
            self.chat_connections[chat_id][user_id] = []

        # Добавляем все активные соединения пользователя в чат
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                if websocket not in self.chat_connections[chat_id][user_id]:
                    self.chat_connections[chat_id][user_id].append(websocket)

        logging.info(f"User {user_id} joined chat {chat_id}")

    async def leave_chat(self, user_id: UUID, chat_id: UUID):
        """Покидание чата"""
        if (
            chat_id in self.chat_connections
            and user_id in self.chat_connections[chat_id]
        ):
            del self.chat_connections[chat_id][user_id]
            logging.info(f"User {user_id} left chat {chat_id}")

    async def send_personal_message(self, message: dict, user_id: UUID):
        """Отправка личного сообщения пользователю"""
        if user_id in self.active_connections:
            disconnected_sockets = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logging.error(f"Error sending message to user {user_id}: {e}")
                    disconnected_sockets.append(websocket)

            # Удаляем неактивные соединения
            for socket in disconnected_sockets:
                self.disconnect(socket, user_id)

    async def send_chat_message(
        self, message: dict, chat_id: UUID, exclude_user: UUID = None
    ):
        """Отправка сообщения всем участникам чата"""
        if chat_id not in self.chat_connections:
            return

        disconnected_sockets = []

        for user_id, websockets in self.chat_connections[chat_id].items():
            # Исключаем отправителя, если нужно
            if exclude_user and user_id == exclude_user:
                continue

            for websocket in websockets:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logging.error(
                        f"Error sending message to user {user_id} in chat {chat_id}: {e}"
                    )
                    disconnected_sockets.append((websocket, user_id))

        # Удаляем неактивные соединения
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

    def is_user_online(self, user_id: UUID) -> bool:
        """Проверить, онлайн ли пользователь"""
        return (
            user_id in self.active_connections
            and len(self.active_connections[user_id]) > 0
        )


connetion_manager = ConnectionManager()
