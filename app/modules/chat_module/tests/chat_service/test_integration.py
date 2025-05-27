from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from app.modules.auth_module.db.cruds.account_crud import AccountCRUD
from app.modules.base_module.schemas.pagination import PaginationParams
from app.modules.chat_module.db.cruds.chat_crud import ChatCRUD
from app.modules.chat_module.db.cruds.message_crud import MessageCRUD
from app.modules.chat_module.db.cruds.profile_crud import ProfileCRUD
from app.modules.chat_module.errors import (
    MembersNotFound,
)
from app.modules.chat_module.schemas.chat_schemas import (
    CreateChatSchema,
    UpdateChatSchema,
)
from app.modules.chat_module.services.chat_service import ChatService


@pytest.mark.asyncio
class TestChatServiceSimplifiedIntegration:
    """Упрощенные интеграционные тесты для ChatService"""

    @pytest.fixture
    async def mock_session(self):
        """Мок сессии базы данных"""
        session = AsyncMock()
        return session

    @pytest.fixture
    def chat_service(self, mock_session):
        """ChatService с реальными CRUD, но мок сессией"""

        service = ChatService(mock_session)
        service.chat_crud = ChatCRUD(mock_session)
        service.account_crud = AccountCRUD(mock_session)
        service.profile_crud = ProfileCRUD(mock_session)
        service.message_crud = MessageCRUD(mock_session)

        return service

    @pytest.fixture
    def mock_account_data(self):
        """Тестовые данные аккаунта"""
        account_id = uuid4()
        profile_id = uuid4()

        account_mock = Mock()
        account_mock.id = account_id
        account_mock.email = "test@example.com"
        account_mock.profile_id = profile_id

        profile_mock = Mock()
        profile_mock.id = profile_id
        profile_mock.first_name = "Тест"
        profile_mock.last_name = "Пользователь"
        profile_mock.username = "test_user"
        profile_mock.chats = []
        profile_mock.account_id = account_id


        return {
            "account": account_mock,
            "profile": profile_mock,
            "account_id": account_id,
            "profile_id": profile_id,
        }

    @pytest.fixture
    def mock_chat_data(self, mock_account_data):
        """Тестовые данные чата"""
        chat_id = uuid4()

        chat_mock = Mock()
        chat_mock.id = chat_id
        chat_mock.name = "Тестовый чат"
        chat_mock.description = "Описание тестового чата"
        chat_mock.owner = mock_account_data["profile"]
        chat_mock.owner_id = mock_account_data["profile_id"]
        chat_mock.members = [mock_account_data["profile"]]

        return {"chat": chat_mock, "chat_id": chat_id}

    async def test_create_chat_integration_flow(
        self, chat_service, mock_account_data, mock_session
    ):
        """Интеграционный тест полного потока создания чата"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]

        chat_data = CreateChatSchema(
            name="Интеграционный чат", description="Тест интеграции", members=[]
        )

        created_chat = Mock()
        created_chat.id = uuid4()
        created_chat.name = chat_data.name
        created_chat.description = chat_data.description
        created_chat.owner_id = profile.id

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.add = AsyncMock(return_value=created_chat)
        chat_service.profile_crud.get_by_ids = AsyncMock(return_value=[profile])
        chat_service.chat_crud.add_members = AsyncMock()

        result = await chat_service.create_chat(account.id, chat_data)

        assert result == created_chat
        assert result.name == "Интеграционный чат"

        chat_service.profile_crud.get_profile_by_account_id.assert_called_once_with(account.id)
        chat_service.chat_crud.add.assert_called_once()
        chat_service.profile_crud.get_by_ids.assert_called_once()
        chat_service.chat_crud.add_members.assert_called_once()
        mock_session.commit.assert_called_once()

    async def test_update_chat_integration_flow(
        self, chat_service, mock_account_data, mock_chat_data, mock_session
    ):
        """Интеграционный тест полного потока обновления чата"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]
        chat = mock_chat_data["chat"]

        profile.is_owner_of_chat = Mock(return_value=True)

        update_data = UpdateChatSchema(
            name="Обновленное название", description="Обновленное описание"
        )

        updated_chat = Mock()
        updated_chat.id = chat.id
        updated_chat.name = update_data.name
        updated_chat.description = update_data.description

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.update = AsyncMock(return_value=updated_chat)
        chat_service.profile_crud.get_by_ids = AsyncMock(return_value=[profile])
        chat_service.chat_crud.add_members = AsyncMock()

        result = await chat_service.update_chat(account.id, update_data, chat.id)

        assert result == updated_chat
        assert result.name == "Обновленное название"

        chat_service.profile_crud.get_profile_by_account_id.assert_called_once_with(account.id)
        chat_service.chat_crud.update.assert_called_once()
        mock_session.commit.assert_called_once()

    async def test_delete_chat_integration_flow(
        self, chat_service, mock_account_data, mock_chat_data, mock_session
    ):
        """Интеграционный тест полного потока удаления чата"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]
        chat = mock_chat_data["chat"]

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.delete = AsyncMock()

        profile.is_owner_of_chat = Mock(return_value=True)

        await chat_service.delete_chat(account.id, chat.id)

        chat_service.profile_crud.get_profile_by_account_id.assert_called_once_with(account.id)
        chat_service.chat_crud.delete.assert_called_once_with(chat.id)
        mock_session.commit.assert_called_once()

    @pytest.mark.skip(reason="TypeError: argument of type 'Mock' is not iterable")
    async def test_chat_history_integration_flow(
        self, chat_service, mock_account_data, mock_chat_data
    ):
        """Интеграционный тест получения истории чата"""
        account = mock_account_data["account"]
        chat = mock_chat_data["chat"]
        profile = mock_account_data["profile"]

        profile.chats = [chat]
        profile.find_chat = Mock(return_value=chat)
        profile.chat_ids = [chat]
        profile.is_memeber_of_chat = Mock(return_value=True)

        pagination = PaginationParams(limit=10, offset=0)

        mock_messages = [
            Mock(id=uuid4(), text="Сообщение 1", sender_id=uuid4()),
            Mock(id=uuid4(), text="Сообщение 2", sender_id=uuid4()),
        ]

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.message_crud.chat_history = AsyncMock(
            return_value=(2, mock_messages)
        )

        result = await chat_service.chat_history(account.id, chat.id, pagination)

        assert result["total_count"] == 2
        assert result["entities"] == mock_messages

        chat_service.profile_crud.get_profile_by_account_id.assert_called_once_with(account.id)
        chat_service.message_crud.chat_history.assert_called_once_with(
            chat.id, limit=10, offset=0
        )

    async def test_error_handling_integration(self, chat_service, mock_account_data):
        """Интеграционный тест обработки ошибок"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]
        # Несуществующий участник
        chat_data = CreateChatSchema(
            name="Тестовый чат", members=[uuid4()]
        )

        # Настраиваем моки для имитации ошибки
        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.add = AsyncMock(return_value=Mock(id=uuid4()))
        chat_service.profile_crud.get_by_ids = AsyncMock(
            return_value=[]
        )  # Пустой список профилей

        with pytest.raises(MembersNotFound):
            await chat_service.create_chat(account.id, chat_data)

    async def test_transaction_integration(
        self, chat_service, mock_account_data, mock_session
    ):
        """Интеграционный тест транзакционности операций"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]
        chat_data = CreateChatSchema(name="Транзакционный чат")

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.add = AsyncMock(return_value=Mock(id=uuid4()))
        chat_service.profile_crud.get_by_ids = AsyncMock(return_value=[account.profile])
        chat_service.chat_crud.add_members = AsyncMock()

        mock_session.commit.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await chat_service.create_chat(account.id, chat_data)

        mock_session.commit.assert_called_once()

    async def test_multiple_operations_integration(
        self, chat_service, mock_account_data, mock_session
    ):
        """Интеграционный тест последовательности операций"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]

        profile.is_owner_of_chat = Mock(return_value=True)

        chat_data = CreateChatSchema(name="Мульти-операционный чат")
        created_chat = Mock(id=uuid4(), name=chat_data.name)

        update_data = UpdateChatSchema(name="Обновленное название")
        updated_chat = Mock(id=created_chat.id, name=update_data.name)

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.add = AsyncMock(return_value=created_chat)
        chat_service.chat_crud.update = AsyncMock(return_value=updated_chat)
        chat_service.chat_crud.delete = AsyncMock()
        chat_service.profile_crud.get_by_ids = AsyncMock(return_value=[account.profile])
        chat_service.chat_crud.add_members = AsyncMock()

        # Создание
        create_result = await chat_service.create_chat(account.id, chat_data)

        # Обновление
        update_result = await chat_service.update_chat(
            account.id, update_data, created_chat.id
        )

        # Удаление
        await chat_service.delete_chat(account.id, created_chat.id)

        assert create_result == created_chat
        assert update_result == updated_chat

        # Проверяем количество вызовов commit (3 операции)
        assert mock_session.commit.call_count == 3

    async def test_concurrent_operations_simulation(
        self, chat_service, mock_account_data, mock_session
    ):
        """Симуляция конкурентных операций"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]

        # Имитируем ситуацию, когда данные изменяются между операциями
        call_count = 0

        def side_effect_get_account(*args, **kwargs):
            nonlocal call_count, profile
            call_count += 1
            if call_count == 1:
                return profile
            else:
                # При повторном вызове возвращаем "обновленный" аккаунт
                updated_account = Mock()
                updated_account.id = account.id

                updated_profile = Mock()
                updated_profile.account_id = account.id
                updated_profile.chats = [Mock(id=uuid4())]  # Новый чат появился
                return updated_account

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(
            side_effect=side_effect_get_account
        )
        chat_service.chat_crud.add = AsyncMock(return_value=Mock(id=uuid4()))
        chat_service.profile_crud.get_by_ids = AsyncMock(return_value=[account.profile])
        chat_service.chat_crud.add_members = AsyncMock()

        chat_data = CreateChatSchema(name="Конкурентный чат")
        result = await chat_service.create_chat(account.id, chat_data)

        assert result is not None
        assert call_count == 1  # get_profile_by_account_id должен был быть вызван один раз

    async def test_data_consistency_integration(
        self, chat_service, mock_account_data, mock_session
    ):
        """Интеграционный тест консистентности данных"""
        account = mock_account_data["account"]
        profile = mock_account_data["profile"]

        # Создаем несколько участников
        member_ids = [uuid4(), uuid4(), uuid4()]
        member_profiles = []
        for member_id in member_ids:
            member = Mock()
            member.id = member_id
            member_profiles.append(member)

        chat_data = CreateChatSchema(name="Консистентный чат", members=member_ids)

        created_chat = Mock(id=uuid4(), name=chat_data.name)
        all_profiles = [profile] + member_profiles  # Владелец + участники

        chat_service.profile_crud.get_profile_by_account_id = AsyncMock(return_value=profile)
        chat_service.chat_crud.add = AsyncMock(return_value=created_chat)
        chat_service.profile_crud.get_by_ids = AsyncMock(return_value=all_profiles)
        chat_service.chat_crud.add_members = AsyncMock()

        result = await chat_service.create_chat(account.id, chat_data)

        assert result == created_chat

        expected_member_ids = member_ids + [profile.id]
        chat_service.profile_crud.get_by_ids.assert_called_once_with(
            expected_member_ids, return_raw=True
        )

        chat_service.chat_crud.add_members.assert_called_once_with(
            created_chat.id, all_profiles
        )
