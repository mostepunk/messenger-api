import asyncio
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi import WebSocketDisconnect

from app.modules.base_module.db.errors import ItemNotFoundError
from app.modules.chat_module.services.websocket_service import WebsocketService


class TestWebsocketService:
    """Тесты для WebSocket сервиса"""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def websocket_service(self, mock_session):
        service = WebsocketService(mock_session)
        service.manager = AsyncMock()
        service.account_crud = AsyncMock()
        service.message_crud = AsyncMock()
        service.chat_crud = AsyncMock()
        service.dedup_service = AsyncMock()
        return service

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock()
        websocket.client_state = 1  # CONNECTED
        return websocket

    @pytest.fixture
    def mock_account_data(self):
        """Фикстура с тестовыми данными аккаунта"""
        account_id = uuid4()
        profile_id = uuid4()

        account = Mock()
        account.id = account_id
        account.profile = Mock()
        account.profile.id = profile_id

        return {"account": account, "account_id": account_id, "profile_id": profile_id}

    async def test_authorize_account_success(
        self, websocket_service, mock_account_data
    ):
        """Тест успешной авторизации через WebSocket"""
        auth_message = '{"type": "auth", "token": "valid_token"}'
        mock_account = mock_account_data["account"]

        with patch(
            "app.modules.chat_module.services.websocket_service.authenticate_websocket_user"
        ) as mock_auth:
            mock_auth.return_value = Mock(id=mock_account.id)
            websocket_service.account_crud.get_by_id.return_value = mock_account

            result = await websocket_service.authorize_account(auth_message)

            assert result == mock_account
            mock_auth.assert_called_once_with("valid_token")
            websocket_service.account_crud.get_by_id.assert_called_once_with(
                mock_account.id
            )

    async def test_authorize_account_invalid_token(self, websocket_service):
        """Тест неуспешной авторизации с невалидным токеном"""
        auth_message = '{"type": "auth", "token": "invalid_token"}'

        with patch(
            "app.modules.chat_module.services.websocket_service.authenticate_websocket_user"
        ) as mock_auth:
            mock_auth.return_value = None

            result = await websocket_service.authorize_account(auth_message)

            assert result is None

    async def test_authorize_account_invalid_json(self, websocket_service):
        """Тест обработки невалидного JSON при авторизации"""
        auth_message = "invalid json"

        result = await websocket_service.authorize_account(auth_message)

        assert result is None

    async def test_authorize_account_wrong_message_type(self, websocket_service):
        """Тест обработки сообщения с неправильным типом"""
        auth_message = '{"type": "not_auth", "token": "some_token"}'

        result = await websocket_service.authorize_account(auth_message)

        assert result is None

    # @pytest.mark.skip("Разобраться почему не отправляет сообщения")
    async def test_auto_join_chat_success(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест успешного автоматического присоединения к чату"""
        chat_id = uuid4()
        profile_id = mock_account_data["profile_id"]

        mock_chat = Mock()
        mock_chat.members = [Mock(id=profile_id), Mock(id=uuid4())]

        websocket_service.chat_crud.get_by_id.return_value = mock_chat
        websocket_service.manager.profile_has_multiple_devices_in_chat.return_value = (
            False
        )

        result = await websocket_service.auto_join_chat(
            chat_id, profile_id, mock_websocket
        )

        assert result is True
        websocket_service.manager.join_chat.assert_called_once_with(profile_id, chat_id)

        websocket_service.manager.send_chat_message.assert_called_once()
        call_args = websocket_service.manager.send_chat_message.call_args[0]
        assert call_args[0]["type"] == "user_joined"
        assert call_args[1] == chat_id
        assert (
            websocket_service.manager.send_chat_message.call_args[1]["exclude_user"]
            == profile_id
        )

    async def test_auto_join_chat_not_member(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест присоединения к чату, где пользователь не является участником"""
        chat_id = uuid4()
        profile_id = mock_account_data["profile_id"]

        # Мокаем чат без данного пользователя
        mock_chat = Mock()
        mock_chat.members = [Mock(id=uuid4()), Mock(id=uuid4())]

        websocket_service.chat_crud.get_by_id.return_value = mock_chat

        result = await websocket_service.auto_join_chat(
            chat_id, profile_id, mock_websocket
        )

        assert result is False
        websocket_service.manager.close_as_not_a_member.assert_called_once_with(
            mock_websocket
        )

    async def test_auto_join_chat_not_found(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест присоединения к несуществующему чату"""

        chat_id = uuid4()
        profile_id = mock_account_data["profile_id"]

        websocket_service.chat_crud.get_by_id.side_effect = ItemNotFoundError()

        result = await websocket_service.auto_join_chat(
            chat_id, profile_id, mock_websocket
        )

        assert result is False
        websocket_service.manager.close_chat_not_found.assert_called_once_with(
            mock_websocket
        )

    async def test_auto_join_chat_multiple_devices(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест присоединения к чату с нескольких устройств"""
        chat_id = uuid4()
        profile_id = mock_account_data["profile_id"]

        mock_chat = Mock()
        mock_chat.members = [Mock(id=profile_id)]

        websocket_service.chat_crud.get_by_id.return_value = mock_chat
        websocket_service.manager.profile_has_multiple_devices_in_chat.return_value = (
            True
        )

        result = await websocket_service.auto_join_chat(
            chat_id, profile_id, mock_websocket
        )

        assert result is True
        # Уведомление о входе в чат не должно отправляться для дополнительного устройства
        websocket_service.manager.send_chat_message.assert_not_called()

    async def test_send_chat_history(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест отправки истории чата"""
        chat_id = uuid4()
        profile_id = mock_account_data["profile_id"]

        # Мокаем сообщения
        mock_messages = [
            Mock(
                id=uuid4(),
                text="Message 1",
                model_dump=Mock(return_value={"id": "1", "text": "Message 1"}),
            ),
            Mock(
                id=uuid4(),
                text="Message 2",
                model_dump=Mock(return_value={"id": "2", "text": "Message 2"}),
            ),
        ]

        websocket_service.message_crud.chat_history.return_value = (2, mock_messages)

        await websocket_service.send_chat_history(chat_id, profile_id, mock_websocket)

        # Проверяем, что сообщение с историей было отправлено
        websocket_service.manager.send_message_to_socket.assert_called_once()
        call_args = websocket_service.manager.send_message_to_socket.call_args[0]
        assert call_args[0] == mock_websocket
        assert call_args[1]["type"] == "chat_history"
        assert call_args[1]["total_count"] == 2
        assert len(call_args[1]["messages"]) == 2

    async def test_send_chat_history_error(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест обработки ошибки при отправке истории чата"""
        chat_id = uuid4()
        profile_id = mock_account_data["profile_id"]

        websocket_service.message_crud.chat_history.side_effect = Exception(
            "Database error"
        )

        await websocket_service.send_chat_history(chat_id, profile_id, mock_websocket)

        # Должно быть отправлено сообщение об ошибке
        websocket_service.manager.send_message_to_socket.assert_called_once()
        call_args = websocket_service.manager.send_message_to_socket.call_args[0]
        assert call_args[1]["type"] == "error"
        assert "Failed to load chat history" in call_args[1]["message"]

    async def test_handle_send_message_success(
        self, websocket_service, mock_account_data
    ):
        """Тест успешной обработки отправки сообщения"""
        message_data = {"type": "send_message", "text": "Тестовое сообщение"}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем сервис дедупликации
        websocket_service.dedup_service.check_and_prevent_duplicate.return_value = (
            True,
            "message_key",
        )

        # Мокаем создание сообщения
        mock_message = Mock()
        mock_message.id = uuid4()
        mock_message.model_dump.return_value = {
            "id": str(mock_message.id),
            "text": "Тестовое сообщение",
        }
        websocket_service.message_crud.add.return_value = mock_message

        await websocket_service.handle_send_message(message_data, user_id, chat_id)

        # Проверяем последовательность вызовов
        websocket_service.dedup_service.check_and_prevent_duplicate.assert_called_once_with(
            user_id, chat_id, "Тестовое сообщение"
        )
        websocket_service.message_crud.add.assert_called_once()
        websocket_service.session.commit.assert_called_once()
        websocket_service.manager.broadcast_to_chat.assert_called_once()
        websocket_service.dedup_service.mark_message_sent.assert_called_once_with(
            "message_key", mock_message.id
        )

    async def test_handle_send_message_blocked_duplicate(
        self, websocket_service, mock_account_data
    ):
        """Тест блокировки дублирующегося сообщения"""
        message_data = {"type": "send_message", "text": "Дублирующееся сообщение"}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем блокировку дедупликацией
        websocket_service.dedup_service.check_and_prevent_duplicate.return_value = (
            False,
            "Too frequent",
        )

        await websocket_service.handle_send_message(message_data, user_id, chat_id)

        # Проверяем, что сообщение НЕ было создано
        websocket_service.message_crud.add.assert_not_called()
        websocket_service.session.commit.assert_not_called()

        # Проверяем, что было отправлено уведомление об ошибке
        websocket_service.manager.send_personal_message.assert_called_once()
        call_args = websocket_service.manager.send_personal_message.call_args[0]
        assert call_args[0]["type"] == "error"
        assert "Message blocked: Too frequent" in call_args[0]["message"]

    async def test_handle_send_message_empty_text(
        self, websocket_service, mock_account_data
    ):
        """Тест обработки пустого сообщения"""
        message_data = {"type": "send_message", "text": ""}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        await websocket_service.handle_send_message(message_data, user_id, chat_id)

        # Пустое сообщение не должно обрабатываться
        websocket_service.dedup_service.check_and_prevent_duplicate.assert_not_called()
        websocket_service.message_crud.add.assert_not_called()

    async def test_handle_send_message_whitespace_only(
        self, websocket_service, mock_account_data
    ):
        """Тест обработки сообщения из одних пробелов"""
        message_data = {"type": "send_message", "text": "   \t\n  "}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        await websocket_service.handle_send_message(message_data, user_id, chat_id)

        # Сообщение из пробелов не должно обрабатываться
        websocket_service.dedup_service.check_and_prevent_duplicate.assert_not_called()
        websocket_service.message_crud.add.assert_not_called()

    async def test_handle_send_message_database_error(
        self, websocket_service, mock_account_data
    ):
        """Тест обработки ошибки базы данных при отправке сообщения"""
        message_data = {"type": "send_message", "text": "Сообщение с ошибкой"}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        websocket_service.dedup_service.check_and_prevent_duplicate.return_value = (
            True,
            "message_key",
        )
        websocket_service.message_crud.add.side_effect = Exception("Database error")

        await websocket_service.handle_send_message(message_data, user_id, chat_id)

        # Должно быть отправлено сообщение об ошибке
        websocket_service.manager.send_personal_message.assert_called_once()
        call_args = websocket_service.manager.send_personal_message.call_args[0]
        assert call_args[0]["type"] == "error"
        assert "Failed to send message" in call_args[0]["message"]

    @pytest.mark.skip("Надо перепроверить эту логику")
    async def test_handle_leave_chat(self, websocket_service, mock_account_data):
        """Тест обработки покидания чата"""
        message_data = {"type": "leave_chat"}
        profile_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем ситуацию, когда пользователь полностью покидает чат
        websocket_service.manager.profile_is_in_chat.return_value = False

        await websocket_service.handle_leave_chat(message_data, profile_id, chat_id)

        websocket_service.manager.leave_chat.assert_called_once_with(
            profile_id, chat_id
        )
        websocket_service.manager.send_chat_message.assert_not_called()

        # Проверяем содержимое отправленного сообщения
        call_args = websocket_service.manager.send_chat_message.call_args
        assert call_args is None

    async def test_handle_leave_chat_multiple_devices(
        self, websocket_service, mock_account_data
    ):
        """Тест покидания чата одним из устройств"""
        message_data = {"type": "leave_chat"}
        profile_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем ситуацию, когда пользователь остается в чате с других устройств
        websocket_service.manager.profile_is_in_chat.return_value = True

        await websocket_service.handle_leave_chat(message_data, profile_id, chat_id)

        websocket_service.manager.leave_chat.assert_called_once_with(
            profile_id, chat_id
        )
        # Уведомление о покидании чата не должно отправляться
        websocket_service.manager.send_chat_message.assert_not_called()

    async def test_handle_mark_read(self, websocket_service, mock_account_data):
        """Тест обработки отметки сообщений как прочитанных"""
        message_data = {"type": "mark_read", "last_read_message_id": str(uuid4())}
        profile_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем список прочитанных сообщений
        newly_read_ids = [uuid4(), uuid4()]
        websocket_service.message_crud.mark_messages_read_by_last_id.return_value = (
            newly_read_ids
        )

        # Мокаем информацию о сообщениях
        mock_messages = [Mock(sender_id=uuid4()), Mock(sender_id=uuid4())]
        websocket_service.message_crud.get_messages_by_ids.return_value = mock_messages

        await websocket_service.handle_mark_read(message_data, profile_id, chat_id)

        websocket_service.message_crud.mark_messages_read_by_last_id.assert_called_once()
        websocket_service.session.commit.assert_called_once()
        websocket_service.manager.broadcast_to_chat.assert_called_once()

        # Проверяем, что отправители получили персональные уведомления
        assert websocket_service.manager.send_personal_message.call_count == 2

    async def test_handle_mark_read_no_new_messages(
        self, websocket_service, mock_account_data
    ):
        """Тест отметки прочитанными когда нет новых сообщений"""
        message_data = {"type": "mark_read", "last_read_message_id": str(uuid4())}
        profile_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем пустой список прочитанных сообщений
        websocket_service.message_crud.mark_messages_read_by_last_id.return_value = []

        await websocket_service.handle_mark_read(message_data, profile_id, chat_id)

        # Уведомления не должны отправляться
        websocket_service.manager.broadcast_to_chat.assert_not_called()
        websocket_service.manager.send_personal_message.assert_not_called()

    async def test_handle_mark_single_read(self, websocket_service, mock_account_data):
        """Тест отметки одного сообщения как прочитанного"""
        message_id = uuid4()
        message_data = {"type": "mark_single_read", "message_id": str(message_id)}
        profile_id = mock_account_data["profile_id"]

        # Мокаем сообщение с отправителем
        mock_message = Mock()
        mock_message.sender = Mock()
        mock_message.sender.id = uuid4()

        websocket_service.message_crud.mark_as_read_by_profile.return_value = True
        websocket_service.message_crud.get_by_id.return_value = mock_message

        await websocket_service.handle_mark_single_read(message_data, profile_id)

        websocket_service.message_crud.mark_as_read_by_profile.assert_called_once_with(
            message_id, profile_id
        )
        websocket_service.manager.send_personal_message.assert_called_once()

        # Проверяем содержимое уведомления
        call_args = websocket_service.manager.send_personal_message.call_args[0]
        assert call_args[0]["type"] == "message_read"
        assert call_args[0]["message_id"] == str(message_id)
        assert call_args[1] == mock_message.sender.id

    async def test_handle_typing_indicator(self, websocket_service, mock_account_data):
        """Тест обработки индикатора печати"""
        message_data = {"type": "typing", "is_typing": True}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        await websocket_service.handle_typing(message_data, user_id, chat_id)

        websocket_service.manager.send_chat_message.assert_called_once()

        call_args = websocket_service.manager.send_chat_message.call_args[0]
        assert call_args[0]["type"] == "typing"
        assert call_args[0]["is_typing"] is True
        assert call_args[0]["user_id"] == str(user_id)
        assert call_args[1] == chat_id
        assert (
            websocket_service.manager.send_chat_message.call_args[1]["exclude_user"]
            == user_id
        )

    async def test_handle_get_unread_count(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест получения количества непрочитанных сообщений"""
        profile_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        websocket_service.message_crud.get_unread_count_for_user.return_value = 5

        await websocket_service.handle_get_unread_count(
            profile_id, mock_websocket, chat_id
        )

        websocket_service.message_crud.get_unread_count_for_user.assert_called_once_with(
            chat_id, profile_id
        )
        websocket_service.manager.send_message_to_socket.assert_called_once()

        # Проверяем содержимое ответа
        call_args = websocket_service.manager.send_message_to_socket.call_args[0]
        assert call_args[1]["type"] == "unread_count"
        assert call_args[1]["count"] == 5

    async def test_handle_websocket_message_unknown_type(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест обработки неизвестного типа сообщения"""
        message_data = {"type": "unknown_type", "data": "some data"}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        await websocket_service.handle_websocket_message(
            message_data, user_id, mock_websocket, chat_id
        )

        # Должно быть отправлено сообщение об ошибке
        websocket_service.manager.send_message_to_socket.assert_called_once()
        call_args = websocket_service.manager.send_message_to_socket.call_args[0]
        assert call_args[1]["type"] == "error"
        assert "Unknown message type: unknown_type" in call_args[1]["message"]

    async def test_handle_websocket_message_exception(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест обработки исключения при обработке WebSocket сообщения"""
        message_data = {"type": "send_message", "text": "test"}
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Мокаем исключение при обработке
        websocket_service.dedup_service.check_and_prevent_duplicate.side_effect = (
            Exception("Test error")
        )

        await websocket_service.handle_websocket_message(
            message_data, user_id, mock_websocket, chat_id
        )

        # Должно быть отправлено сообщение об ошибке
        websocket_service.manager.send_personal_message.assert_called_once()
        call_args = websocket_service.manager.send_personal_message.call_args[0]
        assert call_args[0]["type"] == "error"
        assert "Failed to send message" in call_args[0]["message"]

    async def test_handle_disconnect(self, websocket_service, mock_account_data):
        """Тест обработки отключения пользователя"""
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        await websocket_service.handle_disconnect(user_id, chat_id)

        websocket_service.manager.send_chat_message.assert_called_once()

        call_args = websocket_service.manager.send_chat_message.call_args[0]
        assert call_args[0]["type"] == "user_disconnected"
        assert call_args[0]["user_id"] == str(user_id)
        assert call_args[1] == chat_id
        assert (
            websocket_service.manager.send_chat_message.call_args[1]["exclude_user"]
            == user_id
        )

    @patch("app.modules.chat_module.services.websocket_service.config")
    async def test_handle_incoming_connection_full_flow(
        self, mock_config, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест полного потока обработки входящего соединения"""
        mock_config.environment = "LOCAL"

        chat_id = uuid4()
        mock_account = mock_account_data["account"]

        # Мокаем последовательность операций
        auth_message = '{"type": "auth", "token": "valid_token"}'
        mock_websocket.receive_text.side_effect = [
            auth_message,
            '{"type": "send_message", "text": "Hello"}',
            WebSocketDisconnect(),
        ]

        websocket_service.authorize_account = AsyncMock(return_value=mock_account)
        websocket_service.auto_join_chat = AsyncMock(return_value=True)
        websocket_service.send_chat_history = AsyncMock()
        websocket_service.handle_websocket_message = AsyncMock()
        websocket_service.handle_disconnect = AsyncMock()

        websocket_service.manager.receive_message_from_socket.side_effect = [
            {"type": "send_message", "text": "Hello"},
            WebSocketDisconnect(),
        ]

        await websocket_service.handle_incoming_connection(mock_websocket, chat_id)

        # Проверяем последовательность вызовов
        mock_websocket.accept.assert_called_once()
        websocket_service.authorize_account.assert_called_once()
        websocket_service.manager.connect.assert_called_once()
        websocket_service.manager.user_authorized.assert_called_once()
        websocket_service.auto_join_chat.assert_called_once()
        websocket_service.send_chat_history.assert_called_once()
        websocket_service.handle_websocket_message.assert_called_once()
        websocket_service.handle_disconnect.assert_called_once()
        websocket_service.manager.disconnect.assert_called_once()

    async def test_handle_incoming_connection_auth_failed(
        self, websocket_service, mock_websocket
    ):
        """Тест обработки неуспешной авторизации"""
        chat_id = uuid4()
        auth_message = '{"type": "auth", "token": "invalid_token"}'

        mock_websocket.receive_text.return_value = auth_message
        websocket_service.authorize_account = AsyncMock(return_value=None)

        await websocket_service.handle_incoming_connection(mock_websocket, chat_id)

        # Проверяем, что соединение было закрыто из-за неуспешной авторизации
        websocket_service.manager.close_as_unauthorized.assert_called_once_with(
            mock_websocket
        )

    async def test_handle_incoming_connection_join_failed(
        self, websocket_service, mock_websocket, mock_account_data
    ):
        """Тест обработки неуспешного присоединения к чату"""
        chat_id = uuid4()
        mock_account = mock_account_data["account"]
        auth_message = '{"type": "auth", "token": "valid_token"}'

        mock_websocket.receive_text.return_value = auth_message
        websocket_service.authorize_account = AsyncMock(return_value=mock_account)
        websocket_service.auto_join_chat = AsyncMock(return_value=False)

        await websocket_service.handle_incoming_connection(mock_websocket, chat_id)

        # Проверяем, что пользователь был отключен после неуспешного присоединения
        websocket_service.manager.disconnect.assert_called_once()

    async def test_handle_incoming_connection_exception(
        self, websocket_service, mock_websocket
    ):
        """Тест обработки исключения во время WebSocket соединения"""
        chat_id = uuid4()

        # Мокаем исключение при получении сообщения
        mock_websocket.receive_text.side_effect = Exception("Connection error")

        await websocket_service.handle_incoming_connection(mock_websocket, chat_id)

        # Проверяем, что соединение было закрыто из-за внутренней ошибки
        websocket_service.manager.close_as_internal_error.assert_called_once_with(
            mock_websocket
        )

    async def test_message_filtering_and_validation(
        self, websocket_service, mock_account_data
    ):
        """Тест фильтрации и валидации сообщений"""
        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Тест с отсутствующим полем text
        message_data_no_text = {"type": "send_message"}
        await websocket_service.handle_send_message(
            message_data_no_text, user_id, chat_id
        )
        websocket_service.dedup_service.check_and_prevent_duplicate.assert_not_called()

        # Тест с None в поле text
        message_data_none_text = {"type": "send_message", "text": None}
        await websocket_service.handle_send_message(
            message_data_none_text, user_id, chat_id
        )
        websocket_service.dedup_service.check_and_prevent_duplicate.assert_not_called()

        # Тест с валидным текстом
        websocket_service.dedup_service.check_and_prevent_duplicate.return_value = (
            True,
            "key",
        )
        mock_message = Mock()
        mock_message.id = uuid4()
        mock_message.model_dump.return_value = {"id": str(mock_message.id)}
        websocket_service.message_crud.add.return_value = mock_message

        message_data_valid = {"type": "send_message", "text": "Valid message"}
        await websocket_service.handle_send_message(
            message_data_valid, user_id, chat_id
        )
        websocket_service.dedup_service.check_and_prevent_duplicate.assert_called_once()

    async def test_concurrent_message_handling(
        self, websocket_service, mock_account_data
    ):
        """Тест конкурентной обработки сообщений"""

        user_id = mock_account_data["profile_id"]
        chat_id = uuid4()

        # Настраиваем моки
        websocket_service.dedup_service.check_and_prevent_duplicate.return_value = (
            True,
            "key",
        )
        mock_message = Mock()
        mock_message.id = uuid4()
        mock_message.model_dump.return_value = {"id": str(mock_message.id)}
        websocket_service.message_crud.add.return_value = mock_message

        # Создаем несколько одновременных запросов
        message_data = {"type": "send_message", "text": "Concurrent message"}
        tasks = [
            websocket_service.handle_send_message(message_data, user_id, chat_id)
            for _ in range(5)
        ]

        await asyncio.gather(*tasks)

        # Все сообщения должны быть обработаны
        assert websocket_service.message_crud.add.call_count == 5
        assert websocket_service.session.commit.call_count == 5
