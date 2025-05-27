import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI
import json

from app.modules.chat_module.api.routes.chats import router
from app.modules.chat_module.services.chat_service import ChatService
from app.modules.chat_module.schemas.chat_schemas import ChatDBSchema, ChatSchema, DetailedChatSchema
from app.modules.chat_module.schemas.profile_schemas import ProfileDBSchema, ProfileSchema
from app.modules.chat_module.errors import (
    ChatNotFound,
    AccessDenied,
    MembersNotFound,
    ProhibitedToModifyChat
)
from app.modules.auth_module.schemas.account import AccountSchema, AccountDBSchema
from app.modules.chat_module.schemas.message_schema import MessageSchema, MessageDBSchema

AccountDBSchema.model_rebuild()
ChatSchema.model_rebuild()
ChatDBSchema.model_rebuild()
ProfileDBSchema.model_rebuild()
DetailedChatSchema.model_rebuild()
MessageSchema.model_rebuild()
MessageDBSchema.model_rebuild()



@pytest.fixture
def mock_account():
    """Мок аккаунта пользователя"""
    return AccountSchema(
        id=uuid4(),
        email="test@example.com"
    )


@pytest.fixture
def mock_profile():
    """Мок профиля пользователя"""
    return ProfileSchema(
        id=uuid4(),
        first_name="Тест",
        last_name="Пользователь",
        username="test_user"
    )


@pytest.fixture
def mock_chat_db_schema():
    """Мок чата из БД"""
    chat_id = uuid4()
    owner_id = uuid4()

    owner = ProfileSchema(
        id=owner_id,
        first_name="Владелец",
        last_name="Чата",
        username="owner"
    )

    member = ProfileSchema(
        id=uuid4(),
        first_name="Участник",
        last_name="Чата",
        username="member"
    )

    return ChatDBSchema(
        id=chat_id,
        name="Тестовый чат",
        description="Описание тестового чата",
        owner=owner,
        members=[owner, member],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_session():
    """Мок для сессии базы данных"""
    return AsyncMock()

@pytest.fixture
def mock_chat_service(mock_session):
    """Создание экземпляра ChatService с мок-зависимостями"""
    service = ChatService(mock_session)
    service.chat_crud = AsyncMock()
    service.account_crud = AsyncMock()
    service.profile_crud = AsyncMock()
    service.message_crud = AsyncMock()
    return service


@pytest.fixture
def mock_auth_dependency():
    """Мок dependency для авторизации"""
    def _mock_auth():
        return AccountSchema(id=uuid4(), email="test@example.com")
    return _mock_auth


@pytest.fixture
def mock_service_dependency(mock_chat_service):
    """Мок dependency для сервиса"""
    def _mock_service():
        return mock_chat_service
    return _mock_service


class TestChatAPIPositive:
    """Позитивные тесты API чатов"""

    async def test_get_chats_success(self, app, client, mock_chat_service, mock_account, mock_chat_db_schema):
        """Тест успешного получения списка чатов"""
        # Подготовка
        mock_chat_service.account_crud.get_by_id.return_value = [mock_chat_db_schema]

        # Мокаем dependencies
        from app.modules.chat_module.api.routes.chats import get_service, get_account_from_token

        # Переопределяем dependencies
        app.dependency_overrides[get_account_from_token] = lambda: mock_account
        app.dependency_overrides[get_service] = lambda service_class: mock_chat_service

        # Выполнение
        # response = await client.get("/chats/")
        response = await client.get(app.url_path_for("chats:get"))

        # Проверка
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert len(data["data"]) == 1

        chat = data["data"][0]
        assert chat["id"] == str(mock_chat_db_schema.id)
        assert chat["name"] == mock_chat_db_schema.name
        assert chat["description"] == mock_chat_db_schema.description
        assert chat["owner"]["id"] == str(mock_chat_db_schema.owner.id)

        # Проверяем вызов сервиса
        mock_chat_service.accounts_chats.assert_called_once_with(mock_account.id)

    def test_create_chat_success(self, app, client, mock_chat_service, mock_account, mock_chat_db_schema):
        """Тест успешного создания чата"""
        # Подготовка
        mock_chat_service.create_chat.return_value = mock_chat_db_schema

        create_data = {
            "name": "Новый чат",
            "description": "Описание нового чата",
            "members": [str(uuid4()), str(uuid4())]
        }

        # Мокаем dependencies
        from app.modules.chat_module.api.routes.chats import get_service, get_account_from_token

        app.dependency_overrides[get_account_from_token] = lambda: mock_account
        app.dependency_overrides[get_service] = lambda service_class: mock_chat_service

        # Выполнение
        response = client.post("/chats/", json=create_data)

        # Проверка
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        chat = data["data"]
        assert chat["id"] == str(mock_chat_db_schema.id)
        assert chat["name"] == mock_chat_db_schema.name

        # Проверяем вызов сервиса
        mock_chat_service.create_chat.assert_called_once()
        call_args = mock_chat_service.create_chat.call_args
        assert call_args[0][0] == mock_account.id  # account_id
        assert call_args[0][1].name == create_data["name"]  # CreateChatSchema

    def test_get_chat_info_success(self, app, client, mock_chat_service, mock_account, mock_chat_db_schema):
        """Тест успешного получения информации о чате"""
        # Подготовка
        mock_chat_service.chat_info.return_value = mock_chat_db_schema
        chat_id = uuid4()

        # Мокаем dependencies
        from app.modules.chat_module.api.routes.chats import get_service, get_account_from_token

        app.dependency_overrides[get_account_from_token] = lambda: mock_account
        app.dependency_overrides[get_service] = lambda service_class: mock_chat_service

        # Выполнение
        response = client.get(f"/chats/{chat_id}/")

        # Проверка
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        chat = data["data"]
        assert chat["id"] == str(mock_chat_db_schema.id)
        assert "members" in chat
        assert len(chat["members"]) == 2

        # Проверяем вызов сервиса
        mock_chat_service.chat_info.assert_called_once_with(mock_account.id, chat_id)

    def test_update_chat_success(self, app, client, mock_chat_service, mock_account, mock_chat_db_schema):
        """Тест успешного обновления чата"""
        # Подготовка
        updated_chat = mock_chat_db_schema.model_copy()
        updated_chat.name = "Обновленное название"
        mock_chat_service.update_chat.return_value = updated_chat

        chat_id = uuid4()
        update_data = {
            "name": "Обновленное название",
            "description": "Новое описание"
        }

        # Мокаем dependencies
        from app.modules.chat_module.api.routes.chats import get_service, get_account_from_token

        app.dependency_overrides[get_account_from_token] = lambda: mock_account
        app.dependency_overrides[get_service] = lambda service_class: mock_chat_service

        # Выполнение
        response = client.put(f"/chats/{chat_id}/", json=update_data)

        # Проверка
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        chat = data["data"]
        assert chat["name"] == "Обновленное название"

        # Проверяем вызов сервиса
        mock_chat_service.update_chat.assert_called_once()
        call_args = mock_chat_service.update_chat.call_args
        assert call_args[0][0] == mock_account.id  # account_id
        assert call_args[0][1].name == update_data["name"]  # UpdateChatSchema
        assert call_args[0][2] == chat_id  # chat_id

    def test_delete_chat_success(self, app, client, mock_chat_service, mock_account):
        """Тест успешного удаления чата"""
        # Подготовка
        mock_chat_service.delete_chat.return_value = None
        chat_id = uuid4()

        # Мокаем dependencies
        from app.modules.chat_module.api.routes.chats import get_service, get_account_from_token

        app.dependency_overrides[get_account_from_token] = lambda: mock_account
        app.dependency_overrides[get_service] = lambda service_class: mock_chat_service

        # Выполнение
        response = client.delete(f"/chats/{chat_id}/")

        # Проверка
        assert response.status_code == 200

        # Проверяем вызов сервиса
        mock_chat_service.delete_chat.assert_called_once_with(mock_account.id, chat_id)

    def test_chat_history_success(self, app, client, mock_chat_service, mock_account):
        """Тест успешного получения истории чата"""
        # Подготовка
        mock_messages = [
            {
                "id": str(uuid4()),
                "text": "Сообщение 1",
                "sender": {"id": str(uuid4()), "username": "user1"},
                "sent_at": "2025-01-01T12:00:00Z"
            },
            {
                "id": str(uuid4()),
                "text": "Сообщение 2",
                "sender": {"id": str(uuid4()), "username": "user2"},
                "sent_at": "2025-01-01T12:05:00Z"
            }
        ]

        mock_history = {
            "total_count": 2,
            "entities": mock_messages
        }

        mock_chat_service.chat_history.return_value = mock_history
        chat_id = uuid4()

        # Мокаем dependencies
        from app.modules.chat_module.api.routes.chats import get_service, get_account_from_token

        app.dependency_overrides[get_account_from_token] = lambda: mock_account
        app.dependency_overrides[get_service] = lambda service_class: mock_chat_service

        # Выполнение
        response = client.get(f"/chats/{chat_id}/history/?limit=10&offset=0")

        # Проверка
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        history = data["data"]
        assert history["totalCount"] == 2
        assert len(history["entities"]) == 2
        assert history["entities"][0]["text"] == "Сообщение 1"

        # Проверяем вызов сервиса
        mock_chat_service.chat_history.assert_called_once()
        call_args = mock_chat_service.chat_history.call_args
        assert call_args[0][0] == mock_account.id  # account_id
        assert call_args[0][1] == chat_id  # chat_id
        # Проверяем пагинацию
        pagination = call_args[0][2]
        assert pagination.limit == 10
        assert pagination.offset == 0
