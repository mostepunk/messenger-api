import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.chat_module.websoket.connection_manager import ConnectionManager


class TestConnectionManager:
    """Тесты для менеджера WebSocket соединений"""

    @pytest.fixture
    def connection_manager(self):
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock()
        websocket.client_state = 1  # CONNECTED
        return websocket

    @pytest.fixture
    def mock_websocket2(self):
        websocket = AsyncMock()
        websocket.client_state = 1  # CONNECTED
        return websocket

    async def test_connect_user(self, connection_manager, mock_websocket):
        """Тест подключения пользователя"""
        user_id = uuid4()

        await connection_manager.connect(mock_websocket, user_id)

        assert user_id in connection_manager.active_connections
        assert mock_websocket in connection_manager.active_connections[user_id]
        assert connection_manager.is_user_online(user_id) is True

    async def test_connect_multiple_devices(
        self, connection_manager, mock_websocket, mock_websocket2
    ):
        """Тест подключения пользователя с нескольких устройств"""
        user_id = uuid4()

        await connection_manager.connect(mock_websocket, user_id)
        await connection_manager.connect(mock_websocket2, user_id)

        assert len(connection_manager.active_connections[user_id]) == 2
        assert connection_manager.get_user_connection_count(user_id) == 2

    async def test_disconnect_user(self, connection_manager, mock_websocket):
        """Тест отключения пользователя"""
        user_id = uuid4()

        connection_manager.active_connections[user_id].append(mock_websocket)
        await connection_manager.disconnect(mock_websocket, user_id)

        assert user_id not in connection_manager.active_connections
        assert connection_manager.is_user_online(user_id) is False

    async def test_disconnect_one_device_of_many(
        self, connection_manager, mock_websocket, mock_websocket2
    ):
        """Тест отключения одного устройства из нескольких"""
        user_id = uuid4()

        connection_manager.active_connections[user_id] = [
            mock_websocket,
            mock_websocket2,
        ]

        await connection_manager.disconnect(mock_websocket, user_id)

        assert connection_manager.is_user_online(user_id) is True
        assert len(connection_manager.active_connections[user_id]) == 1
        assert mock_websocket2 in connection_manager.active_connections[user_id]

    async def test_join_chat(self, connection_manager, mock_websocket):
        """Тест присоединения к чату"""
        user_id = uuid4()
        chat_id = uuid4()

        # Сначала подключаем пользователя
        await connection_manager.connect(mock_websocket, user_id)

        # Затем присоединяем к чату
        await connection_manager.join_chat(user_id, chat_id)

        assert chat_id in connection_manager.chat_connections
        assert user_id in connection_manager.chat_connections[chat_id]
        assert mock_websocket in connection_manager.chat_connections[chat_id][user_id]
        assert await connection_manager.profile_is_in_chat(chat_id, user_id) is True

    async def test_leave_chat(self, connection_manager, mock_websocket):
        """Тест покидания чата"""
        user_id = uuid4()
        chat_id = uuid4()

        # Подключаем пользователя к чату
        await connection_manager.connect(mock_websocket, user_id)
        await connection_manager.join_chat(user_id, chat_id)

        # Покидаем чат
        await connection_manager.leave_chat(user_id, chat_id)

        assert user_id not in connection_manager.chat_connections.get(chat_id, {})
        assert await connection_manager.profile_is_in_chat(chat_id, user_id) is False

    async def test_leave_chat_single_device(
        self, connection_manager, mock_websocket, mock_websocket2
    ):
        """Тест покидания чата одним устройством"""
        user_id = uuid4()
        chat_id = uuid4()

        # Подключаем два устройства к чату
        await connection_manager.connect(mock_websocket, user_id)
        await connection_manager.connect(mock_websocket2, user_id)
        await connection_manager.join_chat(user_id, chat_id)

        # Одно устройство покидает чат
        await connection_manager.leave_chat_single_device(
            user_id, chat_id, mock_websocket
        )

        # Пользователь должен остаться в чате через второе устройство
        assert await connection_manager.profile_is_in_chat(chat_id, user_id) is True
        assert len(connection_manager.chat_connections[chat_id][user_id]) == 1
        assert mock_websocket2 in connection_manager.chat_connections[chat_id][user_id]

    async def test_send_personal_message(self, connection_manager, mock_websocket):
        """Тест отправки личного сообщения"""
        user_id = uuid4()
        message = {"type": "test", "text": "Личное сообщение"}

        await connection_manager.connect(mock_websocket, user_id)
        await connection_manager.send_personal_message(message, user_id)

        mock_websocket.send_text.assert_called_once_with(json.dumps(message))

    async def test_send_chat_message(
        self, connection_manager, mock_websocket, mock_websocket2
    ):
        """Тест отправки сообщения в чат"""
        user1_id = uuid4()
        user2_id = uuid4()
        chat_id = uuid4()
        message = {"type": "test", "text": "Сообщение в чат"}

        # Подключаем двух пользователей к чату
        await connection_manager.connect(mock_websocket, user1_id)
        await connection_manager.connect(mock_websocket2, user2_id)
        await connection_manager.join_chat(user1_id, chat_id)
        await connection_manager.join_chat(user2_id, chat_id)

        # Отправляем сообщение в чат
        await connection_manager.send_chat_message(message, chat_id)

        # Оба пользователя должны получить сообщение
        mock_websocket.send_text.assert_called_once_with(json.dumps(message))
        mock_websocket2.send_text.assert_called_once_with(json.dumps(message))

    async def test_send_chat_message_exclude_user(
        self, connection_manager, mock_websocket, mock_websocket2
    ):
        """Тест отправки сообщения в чат с исключением отправителя"""
        user1_id = uuid4()
        user2_id = uuid4()
        chat_id = uuid4()
        message = {"type": "test", "text": "Сообщение в чат"}

        await connection_manager.connect(mock_websocket, user1_id)
        await connection_manager.connect(mock_websocket2, user2_id)
        await connection_manager.join_chat(user1_id, chat_id)
        await connection_manager.join_chat(user2_id, chat_id)

        await connection_manager.send_chat_message(
            message, chat_id, exclude_user=user1_id
        )

        mock_websocket.send_text.assert_not_called()
        mock_websocket2.send_text.assert_called_once_with(json.dumps(message))

    async def test_broadcast_to_chat(
        self, connection_manager, mock_websocket, mock_websocket2
    ):
        """Тест рассылки сообщения всем участникам чата"""
        user1_id = uuid4()
        user2_id = uuid4()
        chat_id = uuid4()
        message = {"type": "broadcast", "text": "Рассылка"}

        await connection_manager.connect(mock_websocket, user1_id)
        await connection_manager.connect(mock_websocket2, user2_id)
        await connection_manager.join_chat(user1_id, chat_id)
        await connection_manager.join_chat(user2_id, chat_id)

        await connection_manager.broadcast_to_chat(message, chat_id)

        mock_websocket.send_text.assert_called_once_with(json.dumps(message))
        mock_websocket2.send_text.assert_called_once_with(json.dumps(message))

    def test_get_chat_online_users(self, connection_manager):
        """Тест получения списка онлайн пользователей в чате"""
        chat_id = uuid4()
        user1_id = uuid4()
        user2_id = uuid4()
        user3_id = uuid4()

        connection_manager.chat_connections[chat_id][user1_id] = [AsyncMock()]
        connection_manager.chat_connections[chat_id][user2_id] = [AsyncMock()]

        online_users = connection_manager.get_chat_online_users(chat_id)

        assert len(online_users) == 2
        assert user1_id in online_users
        assert user2_id in online_users
        assert user3_id not in online_users

    def test_get_chat_stats(self, connection_manager):
        """Тест получения статистики чата"""
        chat_id = uuid4()
        user1_id = uuid4()
        user2_id = uuid4()
        user3_id = uuid4()

        connection_manager.chat_connections[chat_id][user1_id] = [
            AsyncMock(),
            AsyncMock(),
        ]
        connection_manager.chat_connections[chat_id][user2_id] = [AsyncMock()]
        connection_manager.chat_connections[chat_id][user3_id] = [
            AsyncMock(),
            AsyncMock(),
            AsyncMock(),
        ]

        stats = connection_manager.get_chat_stats(chat_id)

        assert stats["users"] == 3
        assert stats["connections"] == 6
        assert stats["users_with_multiple_devices"] == 2

    def test_get_chat_stats_empty_chat(self, connection_manager):
        """Тест получения статистики несуществующего чата"""
        chat_id = uuid4()

        stats = connection_manager.get_chat_stats(chat_id)

        assert stats["users"] == 0
        assert stats["connections"] == 0
        assert stats["users_with_multiple_devices"] == 0

    async def test_profile_has_multiple_devices_in_chat(self, connection_manager):
        """Тест проверки наличия нескольких устройств у пользователя в чате"""
        chat_id = uuid4()
        user_id = uuid4()

        # Сначала нет устройств
        assert (
            await connection_manager.profile_has_multiple_devices_in_chat(
                chat_id, user_id
            )
            is False
        )

        # Одно устройство
        connection_manager.chat_connections[chat_id][user_id] = [AsyncMock()]
        assert (
            await connection_manager.profile_has_multiple_devices_in_chat(
                chat_id, user_id
            )
            is False
        )

        # Два устройства
        connection_manager.chat_connections[chat_id][user_id] = [
            AsyncMock(),
            AsyncMock(),
        ]
        assert (
            await connection_manager.profile_has_multiple_devices_in_chat(
                chat_id, user_id
            )
            is True
        )

    async def test_handle_websocket_errors(self, connection_manager):
        """Тест обработки ошибок WebSocket"""
        user_id = uuid4()
        chat_id = uuid4()
        message = {"type": "test"}

        # Создаем WebSocket, который вызывает ошибку
        mock_websocket_error = AsyncMock()
        mock_websocket_error.send_text.side_effect = Exception("Connection lost")

        # Подключаем пользователя
        connection_manager.active_connections[user_id] = [mock_websocket_error]
        connection_manager.chat_connections[chat_id][user_id] = [mock_websocket_error]

        # Отправляем сообщение - не должно падать
        await connection_manager.send_personal_message(message, user_id)
        await connection_manager.send_chat_message(message, chat_id)

        # Пользователь должен быть отключен после ошибки
        assert user_id not in connection_manager.active_connections
        assert user_id not in connection_manager.chat_connections.get(chat_id, {})

    async def test_websocket_close_methods(self, connection_manager):
        """Тест методов закрытия WebSocket соединений"""
        mock_websocket = AsyncMock()
        mock_websocket.client_state = 1  # CONNECTED

        await connection_manager.close_as_unauthorized(mock_websocket)
        mock_websocket.close.assert_called_with(
            code=1008, reason="Authentication failed"
        )

        mock_websocket.reset_mock()
        await connection_manager.close_access_denied(mock_websocket)
        mock_websocket.close.assert_called_with(code=1008, reason="Access denied")

        mock_websocket.reset_mock()
        await connection_manager.close_chat_not_found(mock_websocket)
        mock_websocket.close.assert_called_with(code=1008, reason="Chat not found")

    async def test_message_serialization(self, connection_manager, mock_websocket):
        """Тест сериализации сообщений"""
        user_id = uuid4()

        complex_message = {
            "type": "test",
            "user_id": str(user_id),
            "timestamp": "2023-01-01T00:00:00Z",
            "data": {"count": 42, "active": True, "items": ["item1", "item2"]},
        }

        await connection_manager.connect(mock_websocket, user_id)
        await connection_manager.send_personal_message(complex_message, user_id)

        expected_json = json.dumps(complex_message)
        mock_websocket.send_text.assert_called_once_with(expected_json)
