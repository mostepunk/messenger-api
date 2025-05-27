from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.base_module.schemas.pagination import PaginationParams
from app.modules.chat_module.errors import (
    AccessDenied,
    ChatNotFound,
    MembersNotFound,
    ProhibitedToModifyChat,
)
from app.modules.chat_module.schemas.chat_schemas import (
    CreateChatSchema,
    UpdateChatSchema,
)
from app.modules.chat_module.services.chat_service import ChatService


class TestChatService:
    """Тесты для ChatService"""

    @pytest.fixture
    def mock_session(self):
        """Мок для сессии базы данных"""
        return AsyncMock()

    @pytest.fixture
    def chat_service(self, mock_session):
        """Создание экземпляра ChatService с мок-зависимостями"""
        service = ChatService(mock_session)
        service.chat_crud = AsyncMock()
        service.account_crud = AsyncMock()
        service.profile_crud = AsyncMock()
        service.message_crud = AsyncMock()
        return service

    @pytest.fixture
    def sample_account_id(self):
        """Пример ID аккаунта"""
        return uuid4()

    @pytest.fixture
    def sample_chat_id(self):
        """Пример ID чата"""
        return uuid4()

    @pytest.fixture
    def sample_profile_id(self):
        """Пример ID профиля"""
        return uuid4()

    @pytest.fixture
    def mock_account_db(self, sample_account_id, sample_profile_id):
        """Мок для AccountDBSchema"""
        account = Mock()
        account.id = sample_account_id
        account.profile = Mock()
        account.profile.id = sample_profile_id
        account.profile.chats = []
        account.profile.find_chat = Mock(return_value=None)
        account.profile.chat_ids = []
        return account

    @pytest.fixture
    def mock_chat_db(self, sample_chat_id, sample_profile_id):
        """Мок для ChatDBSchema"""
        chat = Mock()
        chat.id = sample_chat_id
        chat.owner = Mock()
        chat.owner.id = sample_profile_id
        chat.members = []
        return chat

    @pytest.fixture
    def mock_profile_db(self, sample_profile_id):
        """Мок для ProfileModel"""
        profile = Mock()
        profile.id = sample_profile_id
        return profile

    async def test_accounts_chats_success(
        self, chat_service, mock_account_db, sample_account_id
    ):
        """Тест успешного получения чатов аккаунта"""
        mock_chats = [Mock(), Mock()]
        mock_account_db.profile.chats = mock_chats
        chat_service.account_crud.get_by_id.return_value = mock_account_db

        result = await chat_service.accounts_chats(sample_account_id)

        assert result == mock_chats
        chat_service.account_crud.get_by_id.assert_called_once_with(sample_account_id)

    async def test_create_chat_success(
        self, chat_service, mock_account_db, sample_account_id, sample_profile_id
    ):
        """Тест успешного создания чата"""
        member_id = uuid4()
        chat_data = CreateChatSchema(
            name="Test Chat", description="Test Description", members=[member_id]
        )

        mock_created_chat = Mock()
        mock_created_chat.id = uuid4()

        mock_profiles = [Mock(), Mock()]
        mock_profiles[0].id = member_id
        mock_profiles[1].id = sample_profile_id

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.chat_crud.add.return_value = mock_created_chat
        chat_service.profile_crud.get_by_ids.return_value = mock_profiles

        result = await chat_service.create_chat(sample_account_id, chat_data)

        assert result == mock_created_chat
        chat_service.account_crud.get_by_id.assert_called_once_with(sample_account_id)

        # Проверяем, что владелец добавлен в участники
        expected_values = {
            "name": "Test Chat",
            "description": "Test Description",
            "owner_id": sample_profile_id,
        }
        chat_service.chat_crud.add.assert_called_once_with(expected_values)

        # Проверяем, что участники добавлены в чат
        expected_members = [member_id, sample_profile_id]
        chat_service.profile_crud.get_by_ids.assert_called_once_with(
            expected_members, return_raw=True
        )
        chat_service.chat_crud.add_members.assert_called_once_with(
            mock_created_chat.id, mock_profiles
        )
        chat_service.session.commit.assert_called_once()

    async def test_create_chat_members_not_found(
        self, chat_service, mock_account_db, sample_account_id, sample_profile_id
    ):
        """Тест создания чата с несуществующими участниками"""
        member_id = uuid4()
        chat_data = CreateChatSchema(name="Test Chat", members=[member_id])

        mock_created_chat = Mock()
        mock_created_chat.id = uuid4()

        mock_profiles = [Mock()]
        mock_profiles[0].id = sample_profile_id

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.chat_crud.add.return_value = mock_created_chat
        chat_service.profile_crud.get_by_ids.return_value = mock_profiles

        with pytest.raises(MembersNotFound):
            await chat_service.create_chat(sample_account_id, chat_data)

    async def test_delete_chat_success_as_owner(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест успешного удаления чата владельцем"""
        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.is_account_owner = Mock(return_value=True)

        await chat_service.delete_chat(sample_account_id, sample_chat_id)

        chat_service.account_crud.get_by_id.assert_called_once_with(sample_account_id)
        chat_service.is_account_owner.assert_called_once_with(
            mock_account_db, sample_chat_id
        )
        chat_service.chat_crud.delete.assert_called_once_with(sample_chat_id)
        chat_service.session.commit.assert_called_once()

    async def test_delete_chat_not_owner(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест попытки удаления чата не владельцем"""
        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.is_account_owner = Mock(return_value=False)

        with pytest.raises(ProhibitedToModifyChat):
            await chat_service.delete_chat(sample_account_id, sample_chat_id)

    async def test_update_chat_success(
        self,
        chat_service,
        mock_account_db,
        sample_account_id,
        sample_chat_id,
        sample_profile_id,
    ):
        """Тест успешного обновления чата"""
        member_id = uuid4()
        chat_data = UpdateChatSchema(
            name="Updated Chat", description="Updated Description", members=[member_id]
        )

        mock_updated_chat = Mock()
        mock_updated_chat.id = sample_chat_id

        mock_profiles = [Mock(), Mock()]
        mock_profiles[0].id = member_id
        mock_profiles[1].id = sample_profile_id

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.is_account_owner = Mock(return_value=True)
        chat_service.chat_crud.update.return_value = mock_updated_chat
        chat_service.profile_crud.get_by_ids.return_value = mock_profiles

        result = await chat_service.update_chat(
            sample_account_id, chat_data, sample_chat_id
        )

        assert result == mock_updated_chat
        chat_service.account_crud.get_by_id.assert_called_once_with(sample_account_id)
        chat_service.is_account_owner.assert_called_once_with(
            mock_account_db, sample_chat_id
        )

        expected_values = {"name": "Updated Chat", "description": "Updated Description"}
        chat_service.chat_crud.update.assert_called_once_with(
            sample_chat_id, expected_values
        )

        expected_members = [member_id, sample_profile_id]
        chat_service.profile_crud.get_by_ids.assert_called_once_with(
            expected_members, return_raw=True
        )
        chat_service.chat_crud.add_members.assert_called_once_with(
            mock_updated_chat.id, mock_profiles
        )
        chat_service.session.commit.assert_called_once()

    async def test_update_chat_not_owner(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест попытки обновления чата не владельцем"""
        chat_data = UpdateChatSchema(name="Updated Chat")
        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.is_account_owner = Mock(return_value=False)

        with pytest.raises(ProhibitedToModifyChat):
            await chat_service.update_chat(sample_account_id, chat_data, sample_chat_id)

    async def test_update_chat_members_not_found(
        self,
        chat_service,
        mock_account_db,
        sample_account_id,
        sample_chat_id,
        sample_profile_id,
    ):
        """Тест обновления чата с несуществующими участниками"""
        member_id = uuid4()
        chat_data = UpdateChatSchema(name="Updated Chat", members=[member_id])

        mock_updated_chat = Mock()
        mock_updated_chat.id = sample_chat_id

        mock_profiles = [Mock()]
        mock_profiles[0].id = sample_profile_id

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.is_account_owner = Mock(return_value=True)
        chat_service.chat_crud.update.return_value = mock_updated_chat
        chat_service.profile_crud.get_by_ids.return_value = mock_profiles

        with pytest.raises(MembersNotFound):
            await chat_service.update_chat(sample_account_id, chat_data, sample_chat_id)

    async def test_chat_info_success(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест успешного получения информации о чате"""
        mock_chat = Mock()
        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.chat_crud.full_chat_info.return_value = mock_chat

        result = await chat_service.chat_info(sample_account_id, sample_chat_id)

        assert result == mock_chat
        chat_service.account_crud.get_by_id.assert_called_once_with(sample_account_id)
        chat_service.chat_crud.full_chat_info.assert_called_once_with(sample_chat_id)

    async def test_chat_history_success(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест успешного получения истории чата"""
        mock_chat = Mock()
        mock_chat.id = sample_chat_id
        mock_account_db.profile.find_chat.return_value = mock_chat
        mock_account_db.profile.chat_ids = [sample_chat_id]

        pagination = PaginationParams(limit=10, offset=0)
        mock_messages = [Mock(), Mock()]
        total_count = 2

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.message_crud.chat_history.return_value = (
            total_count,
            mock_messages,
        )

        result = await chat_service.chat_history(
            sample_account_id, sample_chat_id, pagination
        )

        expected_result = {"total_count": total_count, "entities": mock_messages}
        assert result == expected_result

        chat_service.account_crud.get_by_id.assert_called_once_with(sample_account_id)
        mock_account_db.profile.find_chat.assert_called_once_with(sample_chat_id)
        chat_service.message_crud.chat_history.assert_called_once_with(
            sample_chat_id, limit=10, offset=0
        )

    async def test_chat_history_chat_not_found(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест получения истории несуществующего чата"""
        mock_account_db.profile.find_chat.return_value = None
        pagination = PaginationParams(limit=10, offset=0)

        chat_service.account_crud.get_by_id.return_value = mock_account_db

        with pytest.raises(ChatNotFound):
            await chat_service.chat_history(
                sample_account_id, sample_chat_id, pagination
            )

    async def test_chat_history_access_denied(
        self, chat_service, mock_account_db, sample_account_id, sample_chat_id
    ):
        """Тест запрета доступа к истории чата"""
        mock_chat = Mock()
        mock_chat.id = sample_chat_id
        mock_account_db.profile.find_chat.return_value = mock_chat
        mock_account_db.profile.chat_ids = []  # Пользователь не участник чата

        pagination = PaginationParams(limit=10, offset=0)
        chat_service.account_crud.get_by_id.return_value = mock_account_db

        with pytest.raises(AccessDenied):
            await chat_service.chat_history(
                sample_account_id, sample_chat_id, pagination
            )

    def test_is_account_owner_true(
        self, chat_service, mock_account_db, sample_chat_id, sample_profile_id
    ):
        """Тест проверки владельца чата - позитивный случай"""
        mock_chat = Mock()
        mock_chat.id = sample_chat_id
        mock_chat.owner = Mock()
        mock_chat.owner.id = sample_profile_id

        mock_account_db.profile.chats = [mock_chat]

        result = chat_service.is_account_owner(mock_account_db, sample_chat_id)

        assert result is True

    def test_is_account_owner_false(
        self, chat_service, mock_account_db, sample_chat_id, sample_profile_id
    ):
        """Тест проверки владельца чата - негативный случай"""
        other_user_id = uuid4()
        mock_chat = Mock()
        mock_chat.id = sample_chat_id
        mock_chat.owner = Mock()
        mock_chat.owner.id = other_user_id  # Другой пользователь владелец

        mock_account_db.profile.chats = [mock_chat]

        result = chat_service.is_account_owner(mock_account_db, sample_chat_id)
        assert result is False

    def test_is_account_owner_chat_not_in_list(
        self, chat_service, mock_account_db, sample_profile_id
    ):
        """Тест проверки владельца для чата, которого нет в списке"""
        non_existent_chat_id = uuid4()
        mock_account_db.profile.chats = []
        result = chat_service.is_account_owner(mock_account_db, non_existent_chat_id)
        assert result is False

    async def test_create_chat_without_members(
        self, chat_service, mock_account_db, sample_account_id, sample_profile_id
    ):
        """Тест создания чата без указания участников"""
        chat_data = CreateChatSchema(name="Test Chat", description="Test Description")

        mock_created_chat = Mock()
        mock_created_chat.id = uuid4()

        mock_profiles = [Mock()]
        mock_profiles[0].id = sample_profile_id

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.chat_crud.add.return_value = mock_created_chat
        chat_service.profile_crud.get_by_ids.return_value = mock_profiles

        result = await chat_service.create_chat(sample_account_id, chat_data)
        assert result == mock_created_chat

        expected_members = [sample_profile_id]
        chat_service.profile_crud.get_by_ids.assert_called_once_with(
            expected_members, return_raw=True
        )

    async def test_update_chat_partial_update(
        self,
        chat_service,
        mock_account_db,
        sample_account_id,
        sample_chat_id,
        sample_profile_id,
    ):
        """Тест частичного обновления чата (только название)"""
        chat_data = UpdateChatSchema(name="Updated Chat Only")

        mock_updated_chat = Mock()
        mock_updated_chat.id = sample_chat_id

        mock_profiles = [Mock()]
        mock_profiles[0].id = sample_profile_id

        chat_service.account_crud.get_by_id.return_value = mock_account_db
        chat_service.is_account_owner = Mock(return_value=True)
        chat_service.chat_crud.update.return_value = mock_updated_chat
        chat_service.profile_crud.get_by_ids.return_value = mock_profiles

        result = await chat_service.update_chat(
            sample_account_id, chat_data, sample_chat_id
        )

        assert result == mock_updated_chat

        expected_values = {"name": "Updated Chat Only"}
        chat_service.chat_crud.update.assert_called_once_with(
            sample_chat_id, expected_values
        )

        # Владелец должен быть добавлен в участники даже при частичном обновлении
        expected_members = [sample_profile_id]
        chat_service.profile_crud.get_by_ids.assert_called_once_with(
            expected_members, return_raw=True
        )
