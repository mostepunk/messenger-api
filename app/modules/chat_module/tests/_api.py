from datetime import datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import ASYNC_SESSION
from app.modules.auth_module.db.models.account import AccountModel
from app.modules.auth_module.dependencies.token import create_access_token
from app.modules.auth_module.utils.password import get_password_hash
from app.modules.chat_module.db.models.chat import MessageModel
from app.modules.chat_module.db.models.profile import (
    ProfileModel,
    ProfilePersonalDataModel,
)
from app.utils.fake_client import fake


class TestChatsE2E:
    """End-to-end тесты для эндпоинта /chats"""

    @pytest.fixture(scope="class")
    async def setup_test_data(self):
        """Создание тестовых данных в базе"""
        async with ASYNC_SESSION() as session:
            accounts = []
            profiles_data = []

            for i in range(4):
                user_id = uuid4()
                profile_id = uuid4()

                # Создаем аккаунт
                account = AccountModel(
                    id=user_id,
                    email=f"e2e_user{i}@example.com",
                    password=get_password_hash("Testpassword123"),
                    is_confirmed=True,
                )
                session.add(account)
                accounts.append(
                    {
                        "id": user_id,
                        "email": account.email,
                        "password": "Testpassword123",
                    }
                )

                # Создаем профиль
                profile = ProfileModel(
                    id=profile_id,
                    account_id=user_id,
                    first_name=f"User{i}",
                    last_name=f"Test{i}",
                    username=f"e2e_user{i}",
                )
                session.add(profile)

                pd = ProfilePersonalDataModel(
                    profile_id=profile_id, phone=f"+799912345{i:02d}"
                )
                session.add(pd)
                profiles_data.append({"id": profile_id, "account_id": user_id})
                session.add(pd)

            await session.commit()
            # Возвращаем данные для тестов
            yield {"accounts": accounts, "profiles": profiles_data}

            # Очистка после тестов
            await self.cleanup_test_data(session, accounts)

    async def cleanup_test_data(self, session: AsyncSession, accounts: list):
        """Очистка тестовых данных"""
        try:
            # Удаляем всех тестовых пользователей (каскадно удалятся связанные данные)
            for account in accounts:
                await session.execute(
                    delete(AccountModel).where(AccountModel.id == account["id"])
                )
            await session.commit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    @pytest.fixture
    async def account1_auth_headers(self, setup_test_data, client):
        """Создание заголовков авторизации для первого пользователя"""
        account = setup_test_data["accounts"][0]
        user_data = {
            "email": account["email"],
            "password": account["password"],
            "fingerprint": "FINGERPRINT1",
        }
        response = await client.post("/accounts/sign-in/", json=user_data)
        assert response.status_code == 200, f"Account {account['email']} Sign-in failed"
        access_token = response.json()["data"]["accessToken"]

        return {"Authorization": f"Bearer {access_token}"}

    @pytest.fixture
    async def account2_auth_headers(self, client, setup_test_data):
        """Создание заголовков авторизации для второго пользователя"""
        account = setup_test_data["accounts"][1]
        user_data = {
            "email": account["email"],
            "password": account["password"],
            "fingerprint": "FINGERPRINT2",
        }
        response = await client.post("/accounts/sign-in/", json=user_data)
        assert response.status_code == 200, f"Account {account['email']} Sign-in failed"
        access_token = response.json()["data"]["accessToken"]

    @pytest.fixture
    async def account3_auth_headers(self, client, setup_test_data):
        """Создание заголовков авторизации для второго пользователя"""
        account = setup_test_data["accounts"][2]
        user_data = {
            "email": account["email"],
            "password": account["password"],
            "fingerprint": "FINGERPRINT2",
        }
        response = await client.post("/accounts/sign-in/", json=user_data)
        assert response.status_code == 200, f"Account {account['email']} Sign-in failed"
        access_token = response.json()["data"]["accessToken"]

    async def create_new_account(self, session):
        """Создание нового аккаунта"""
        account = AccountModel(
            email=fake.email(),
            password=get_password_hash("admin"),
            is_confirmed=True,
        )
        await session.add(account)
        await session.commit()
        return {"email": account.email, "password": "admin"}

    async def test_get_empty_chats_list(self, client, account1_auth_headers):
        """Тест получения пустого списка чатов"""
        response = await client.get("/chats/", headers=account1_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"] == []

    async def test_create_chat_success(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест успешного создания чата"""
        profiles = setup_test_data["profiles"]
        member_profile_id = str(profiles[1]["id"])  # Второй пользователь

        chat_data = {
            "name": "E2E Test Chat",
            "description": "Chat created in e2e test",
            "members": [member_profile_id],
        }

        response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        chat = data["data"]
        assert chat["name"] == "E2E Test Chat"
        assert chat["description"] == "Chat created in e2e test"
        assert "id" in chat
        assert "owner" in chat

        # Сохраняем ID чата для последующих тестов
        return chat["id"]

    async def test_create_chat_without_members(self, client, account1_auth_headers):
        """Тест создания чата без указания участников"""
        chat_data = {
            "name": "Solo Chat",
            "description": "Chat without additional members",
        }

        response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        chat = data["data"]
        assert chat["name"] == "Solo Chat"

    async def test_create_chat_with_nonexistent_members(
        self, client, account1_auth_headers
    ):
        """Тест создания чата с несуществующими участниками"""
        chat_data = {
            "name": "Invalid Chat",
            "members": [str(uuid4()), str(uuid4())],  # Несуществующие UUID
        }

        response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "members not found" in data["error"]["message"].lower()

    async def test_get_chats_list_after_creation(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест получения списка чатов после создания"""
        # Сначала создаем чат
        profiles = setup_test_data["profiles"]
        chat_data = {"name": "List Test Chat", "members": [str(profiles[1]["id"])]}

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        assert create_response.status_code == 200

        # Теперь получаем список чатов
        response = await client.get("/chats/", headers=account1_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) >= 1

        # Проверяем, что наш чат есть в списке
        chat_names = [chat["name"] for chat in data["data"]]
        assert "List Test Chat" in chat_names

    async def test_get_chat_info_success(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест успешного получения информации о чате"""
        # Создаем чат
        profiles = setup_test_data["profiles"]
        chat_data = {
            "name": "Info Test Chat",
            "description": "Chat for info testing",
            "members": [str(profiles[1]["id"]), str(profiles[2]["id"])],
        }

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Получаем информацию о чате
        response = await client.get(f"/chats/{chat_id}/", headers=account1_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        chat = data["data"]
        assert chat["name"] == "Info Test Chat"
        assert chat["description"] == "Chat for info testing"
        assert "members" in chat
        assert len(chat["members"]) == 3  # Владелец + 2 участника
        assert "owner" in chat
        assert "createdAt" in chat
        assert "updatedAt" in chat

    async def test_get_chat_info_not_member(
        self, client, account2_auth_headers, setup_test_data
    ):
        """Тест получения информации о чате, где пользователь не участник"""
        # Создаем чат от первого пользователя без второго в участниках
        profiles = setup_test_data["profiles"]
        user1_token = create_access_token(
            setup_test_data["accounts"][0]["id"],
            setup_test_data["accounts"][0]["email"],
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        chat_data = {
            "name": "Exclusive Chat",
            "members": [str(profiles[2]["id"])],  # Только третий пользователь
        }

        create_response = await client.post(
            "/chats/", json=chat_data, headers=user1_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Пытаемся получить информацию от второго пользователя
        response = await client.get(f"/chats/{chat_id}/", headers=account2_auth_headers)

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"
        assert "access denied" in data["error"]["message"].lower()

    async def test_get_chat_info_nonexistent(self, client, account1_auth_headers):
        """Тест получения информации о несуществующем чате"""
        fake_chat_id = str(uuid4())

        response = await client.get(
            f"/chats/{fake_chat_id}/", headers=account1_auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert "not found" in data["error"]["message"].lower()

    async def test_update_chat_success(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест успешного обновления чата"""
        # Создаем чат
        profiles = setup_test_data["profiles"]
        chat_data = {
            "name": "Original Chat",
            "description": "Original description",
            "members": [str(profiles[1]["id"])],
        }

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Обновляем чат
        update_data = {
            "name": "Updated Chat",
            "description": "Updated description",
            "members": [str(profiles[1]["id"]), str(profiles[2]["id"])],
        }

        response = await client.put(
            f"/chats/{chat_id}/", json=update_data, headers=account1_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        chat = data["data"]
        assert chat["name"] == "Updated Chat"
        assert chat["description"] == "Updated description"

    async def test_update_chat_not_owner(
        self, client, account2_auth_headers, setup_test_data
    ):
        """Тест обновления чата пользователем, который не является владельцем"""
        # Создаем чат от первого пользователя
        profiles = setup_test_data["profiles"]
        user1_token = create_access_token(
            setup_test_data["accounts"][0]["id"],
            setup_test_data["accounts"][0]["email"],
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        chat_data = {"name": "Owner Test Chat", "members": [str(profiles[1]["id"])]}

        create_response = await client.post(
            "/chats/", json=chat_data, headers=user1_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Пытаемся обновить от второго пользователя
        update_data = {"name": "Hacked Chat"}

        response = await client.put(
            f"/chats/{chat_id}/", json=update_data, headers=account2_auth_headers
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"
        assert "prohibited" in data["error"]["message"].lower()

    async def test_delete_chat_success(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест успешного удаления чата"""
        # Создаем чат
        profiles = setup_test_data["profiles"]
        chat_data = {"name": "Chat to Delete", "members": [str(profiles[1]["id"])]}

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Удаляем чат
        response = await client.delete(
            f"/chats/{chat_id}/", headers=account1_auth_headers
        )

        assert response.status_code == 200

        # Проверяем, что чат действительно удален
        get_response = await client.get(
            f"/chats/{chat_id}/", headers=account1_auth_headers
        )
        assert get_response.status_code == 404

    async def test_delete_chat_not_owner(
        self, client, account2_auth_headers, setup_test_data
    ):
        """Тест удаления чата пользователем, который не является владельцем"""
        # Создаем чат от первого пользователя
        profiles = setup_test_data["profiles"]
        user1_token = create_access_token(
            setup_test_data["accounts"][0]["id"],
            setup_test_data["accounts"][0]["email"],
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        chat_data = {"name": "Protected Chat", "members": [str(profiles[1]["id"])]}

        create_response = await client.post(
            "/chats/", json=chat_data, headers=user1_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Пытаемся удалить от второго пользователя
        response = await client.delete(
            f"/chats/{chat_id}/", headers=account2_auth_headers
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"
        assert "prohibited" in data["error"]["message"].lower()

    async def test_chat_history_empty(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест получения пустой истории чата"""
        # Создаем чат
        profiles = setup_test_data["profiles"]
        chat_data = {"name": "Empty History Chat", "members": [str(profiles[1]["id"])]}

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Получаем историю
        response = await client.get(
            f"/chats/{chat_id}/history/", headers=account1_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        history = data["data"]
        assert history["totalCount"] == 0
        assert history["entities"] == []

    async def test_chat_history_with_pagination(
        self, client, account1_auth_headers, setup_test_data
    ):
        """Тест получения истории чата с пагинацией"""
        # Создаем чат
        profiles = setup_test_data["profiles"]
        chat_data = {
            "name": "Pagination Test Chat",
            "members": [str(profiles[1]["id"])],
        }

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Добавляем несколько сообщений в БД напрямую
        async with ASYNC_SESSION() as session:
            chat_uuid = UUID(chat_id)
            sender_id = UUID(str(profiles[0]["id"]))

            for i in range(5):
                message = MessageModel(
                    chat_id=chat_uuid,
                    sender_id=sender_id,
                    text=f"Test message {i+1}",
                    sent_at=datetime.utcnow(),
                )
                session.add(message)
            await session.commit()

        # Получаем историю с пагинацией
        response = await client.get(
            f"/chats/{chat_id}/history/?limit=3&offset=0", headers=account1_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        history = data["data"]
        assert history["totalCount"] == 5
        assert len(history["entities"]) == 3

    async def test_chat_history_not_member(
        self, client, account2_auth_headers, setup_test_data
    ):
        """Тест получения истории чата, где пользователь не участник"""
        # Создаем чат от первого пользователя без второго
        profiles = setup_test_data["profiles"]
        user1_token = create_access_token(
            setup_test_data["accounts"][0]["id"],
            setup_test_data["accounts"][0]["email"],
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        chat_data = {
            "name": "Private History Chat",
            "members": [str(profiles[2]["id"])],
        }

        create_response = await client.post(
            "/chats/", json=chat_data, headers=user1_headers
        )
        chat_id = create_response.json()["data"]["id"]

        # Пытаемся получить историю от второго пользователя
        response = await client.get(
            f"/chats/{chat_id}/history/", headers=account2_auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert "not found" in data["error"]["message"].lower()

    async def test_unauthorized_access(self, client):
        """Тест доступа без авторизации"""
        # Попытка получить список чатов без токена
        response = await client.get("/chats/")
        assert response.status_code == 401

        # Попытка создать чат без токена
        response = await client.post("/chats/", json={"name": "Unauthorized Chat"})
        assert response.status_code == 401

    async def test_invalid_token(self, client):
        """Тест с невалидным токеном"""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}

        response = await client.get("/chats/", headers=invalid_headers)
        assert response.status_code == 401

    async def test_validation_errors(self, client, account1_auth_headers):
        """Тест валидации входных данных"""
        # Пустое название чата
        response = await client.post(
            "/chats/", json={"name": ""}, headers=account1_auth_headers
        )
        assert response.status_code == 422

        # Слишком длинное название
        long_name = "x" * 101
        response = await client.post(
            "/chats/", json={"name": long_name}, headers=account1_auth_headers
        )
        assert response.status_code == 422

        # Слишком длинное описание
        long_description = "x" * 251
        response = await client.post(
            "/chats/",
            json={"name": "Valid Name", "description": long_description},
            headers=account1_auth_headers,
        )
        assert response.status_code == 422

    async def test_invalid_uuid_in_url(self, client, account1_auth_headers):
        """Тест с невалидным UUID в URL"""
        response = await client.get(
            "/chats/invalid-uuid/", headers=account1_auth_headers
        )
        assert response.status_code == 422

    async def test_complex_chat_workflow(
        self,
        client,
        setup_test_data,
        account1_auth_headers,
        account2_auth_headers,
        account3_auth_headers,
    ):
        """Тест комплексного сценария работы с чатами"""
        profiles = setup_test_data["profiles"]
        users = setup_test_data["accounts"]

        # 1. Пользователь 1 создает групповой чат с пользователями 2 и 3
        chat_data = {
            "name": "Team Chat",
            "description": "Our team communication",
            "members": [str(profiles[1]["id"]), str(profiles[2]["id"])],
        }

        create_response = await client.post(
            "/chats/", json=chat_data, headers=account1_auth_headers
        )
        assert create_response.status_code == 200
        chat_id = create_response.json()["data"]["id"]

        # 2. Все участники видят чат в своих списках
        for headers in [
            account1_auth_headers,
            account2_auth_headers,
            account3_auth_headers,
        ]:
            response = await client.get("/chats/", headers=headers)
            assert response.status_code == 200
            chat_names = [chat["name"] for chat in response.json()["data"]]
            assert "Team Chat" in chat_names

        # 3. Все участники могут получить информацию о чате
        for headers in [
            account1_auth_headers,
            account2_auth_headers,
            account3_auth_headers,
        ]:
            response = await client.get(f"/chats/{chat_id}/", headers=headers)
            assert response.status_code == 200
            assert response.json()["data"]["name"] == "Team Chat"

        # 4. Только владелец может обновить чат
        update_data = {"name": "Updated Team Chat"}

        # Пользователь 2 не может обновить
        response = await client.put(
            f"/chats/{chat_id}/", json=update_data, headers=account2_auth_headers
        )
        assert response.status_code == 403

        # Пользователь 1 (владелец) может обновить
        response = await client.put(
            f"/chats/{chat_id}/", json=update_data, headers=account1_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Updated Team Chat"

        # 5. Только владелец может удалить чат
        # Пользователь 3 не может удалить
        response = await client.delete(
            f"/chats/{chat_id}/", headers=account3_auth_headers
        )
        assert response.status_code == 403

        # Пользователь 1 (владелец) может удалить
        response = await client.delete(
            f"/chats/{chat_id}/", headers=account1_auth_headers
        )
        assert response.status_code == 200

        # 6. Чат больше не доступен никому
        for headers in [
            account1_auth_headers,
            account2_auth_headers,
            account3_auth_headers,
        ]:
            response = await client.get(f"/chats/{chat_id}/", headers=headers)
            assert response.status_code == 404
