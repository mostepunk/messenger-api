import asyncio
import json
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth_module.db.models.account import AccountModel
from app.modules.auth_module.utils.password import get_password_hash
from app.modules.chat_module.db.models.chat import ChatModel, MessageModel
from app.modules.chat_module.db.models.profile import ProfileModel


class TestChatAPIE2E:
    """E2E тесты для API chat_module"""

    @pytest.fixture(scope="class")
    async def test_users(self, session: AsyncSession):
        """Создание тестовых пользователей"""
        users_data = []

        for i in range(3):
            # Создаем профиль
            profile = ProfileModel(
                first_name=f"User{i}",
                last_name=f"LastName{i}",
                username=f"testuser{i}",
            )
            session.add(profile)
            await session.flush()

            # Создаем аккаунт
            account = AccountModel(
                email=f"user{i}@test.com",
                password=get_password_hash("testpass123"),
                is_confirmed=True,
                profile_id=profile.id,
            )
            session.add(account)
            await session.flush()

            users_data.append({
                "account_id": account.id,
                "profile_id": profile.id,
                "email": account.email,
                "password": "testpass123",
            })

        await session.commit()
        return users_data

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient, test_users):
        """Получение авторизационных заголовков для всех пользователей"""
        headers = {}

        for i, user in enumerate(test_users):
            response = await client.post("/accounts/sign-in/", json={
                "email": user["email"],
                "password": user["password"],
                "fingerprint": f"test-device-{i}"
            })
            assert response.status_code == 200

            token = response.json()["data"]["access_token"]
            headers[f"user{i}"] = {"Authorization": f"Bearer {token}"}
            print(user)

        return headers

    async def test_chat_full_lifecycle(self, client: AsyncClient, auth_headers, test_users):
        """Тест полного жизненного цикла чата"""
        user0_headers = auth_headers["user0"]
        user1_headers = auth_headers["user1"]
        user2_headers = auth_headers["user2"]

        # 1. Создание чата пользователем 0
        chat_data = {
            "name": "Test Group Chat",
            "description": "E2E test chat",
            "members": [test_users[1]["profile_id"], test_users[2]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        assert response.status_code == 200

        chat_response = response.json()["data"]
        chat_id = chat_response["id"]
        assert chat_response["name"] == "Test Group Chat"
        assert chat_response["description"] == "E2E test chat"

        # 2. Получение списка чатов всеми пользователями
        for i, headers in enumerate([user0_headers, user1_headers, user2_headers]):
            response = await client.get("/chats/", headers=headers)
            assert response.status_code == 200

            chats = response.json()["data"]
            assert len(chats) == 1
            assert chats[0]["id"] == chat_id
            assert chats[0]["name"] == "Test Group Chat"

        # 3. Получение детальной информации о чате
        response = await client.get(f"/chats/{chat_id}/", headers=user0_headers)
        assert response.status_code == 200

        chat_details = response.json()["data"]
        assert len(chat_details["members"]) == 3  # все участники включая владельца
        assert chat_details["owner"]["id"] == test_users[0]["profile_id"]

        # 4. Обновление чата (только владелец)
        update_data = {
            "name": "Updated Chat Name",
            "description": "Updated description"
        }

        response = await client.put(f"/chats/{chat_id}/", json=update_data, headers=user0_headers)
        assert response.status_code == 200

        updated_chat = response.json()["data"]
        assert updated_chat["name"] == "Updated Chat Name"
        assert updated_chat["description"] == "Updated description"

        # 5. Попытка обновления не владельцем (должна провалиться)
        response = await client.put(f"/chats/{chat_id}/", json=update_data, headers=user1_headers)
        assert response.status_code == 403

        # 6. Получение истории чата (пустая)
        response = await client.get(f"/chats/{chat_id}/history/", headers=user0_headers)
        assert response.status_code == 200

        history = response.json()["data"]
        assert history["totalCount"] == 0
        assert history["entities"] == []

    async def test_chat_with_messages_history(self, client: AsyncClient, auth_headers, test_users, session: AsyncSession):
        """Тест работы с историей сообщений"""
        user0_headers = auth_headers["user0"]

        # Создаем чат
        chat_data = {
            "name": "Chat with Messages",
            "members": [test_users[1]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        chat_id = response.json()["data"]["id"]

        # Добавляем сообщения напрямую в БД для тестирования истории
        messages = []
        for i in range(5):
            message = MessageModel(
                chat_id=chat_id,
                sender_id=test_users[0]["profile_id"],
                text=f"Test message {i+1}",
                sent_at=f"2025-01-{i+1:02d}T12:00:00Z"
            )
            session.add(message)
            messages.append(message)

        await session.commit()

        # Получаем историю с пагинацией
        response = await client.get(
            f"/chats/{chat_id}/history/?limit=3&offset=1",
            headers=user0_headers
        )
        assert response.status_code == 200

        history = response.json()["data"]
        assert history["totalCount"] == 5
        assert len(history["entities"]) == 3

        # Проверяем сортировку по времени (последние сообщения первыми)
        messages_texts = [msg["text"] for msg in history["entities"]]
        assert messages_texts == ["Test message 5", "Test message 4", "Test message 3"]

    async def test_chat_permissions(self, client: AsyncClient, auth_headers, test_users):
        """Тест прав доступа к чатам"""
        user0_headers = auth_headers["user0"]
        user1_headers = auth_headers["user1"]
        user2_headers = auth_headers["user2"]

        # Создаем приватный чат между user0 и user1
        chat_data = {
            "name": "Private Chat",
            "members": [test_users[1]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        chat_id = response.json()["data"]["id"]

        # user2 не должен видеть этот чат
        response = await client.get("/chats/", headers=user2_headers)
        chats = response.json()["data"]
        chat_ids = [chat["id"] for chat in chats]
        assert chat_id not in chat_ids

        # user2 не должен иметь доступ к чату
        response = await client.get(f"/chats/{chat_id}/", headers=user2_headers)
        assert response.status_code == 404  # или 403 в зависимости от реализации

        # user2 не должен иметь доступ к истории
        response = await client.get(f"/chats/{chat_id}/history/", headers=user2_headers)
        assert response.status_code in [403, 404]

    async def test_chat_deletion(self, client: AsyncClient, auth_headers, test_users):
        """Тест удаления чата"""
        user0_headers = auth_headers["user0"]
        user1_headers = auth_headers["user1"]

        # Создаем чат
        chat_data = {
            "name": "Chat to Delete",
            "members": [test_users[1]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        chat_id = response.json()["data"]["id"]

        # Участник не может удалить чат
        response = await client.delete(f"/chats/{chat_id}/", headers=user1_headers)
        assert response.status_code == 403

        # Владелец может удалить чат
        response = await client.delete(f"/chats/{chat_id}/", headers=user0_headers)
        assert response.status_code == 200

        # Чат больше не доступен
        response = await client.get(f"/chats/{chat_id}/", headers=user0_headers)
        assert response.status_code == 404

    async def test_chat_member_management(self, client: AsyncClient, auth_headers, test_users):
        """Тест управления участниками чата"""
        user0_headers = auth_headers["user0"]

        # Создаем чат с одним участником
        chat_data = {
            "name": "Expandable Chat",
            "members": [test_users[1]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        chat_id = response.json()["data"]["id"]

        # Добавляем еще одного участника через обновление
        update_data = {
            "members": [test_users[1]["profile_id"], test_users[2]["profile_id"]]
        }

        response = await client.put(f"/chats/{chat_id}/", json=update_data, headers=user0_headers)
        assert response.status_code == 200

        # Проверяем, что участник добавлен
        response = await client.get(f"/chats/{chat_id}/", headers=user0_headers)
        chat_details = response.json()["data"]
        member_ids = [member["id"] for member in chat_details["members"]]

        assert test_users[0]["profile_id"] in member_ids  # владелец
        assert test_users[1]["profile_id"] in member_ids  # старый участник
        assert test_users[2]["profile_id"] in member_ids  # новый участник

    async def test_chat_validation_errors(self, client: AsyncClient, auth_headers):
        """Тест валидации данных чата"""
        user0_headers = auth_headers["user0"]

        # Тест создания чата без названия
        invalid_data = {
            "description": "Chat without name"
        }

        response = await client.post("/chats/", json=invalid_data, headers=user0_headers)
        assert response.status_code == 422

        # Тест с пустым названием
        invalid_data = {
            "name": "",
            "description": "Chat with empty name"
        }

        response = await client.post("/chats/", json=invalid_data, headers=user0_headers)
        assert response.status_code == 422

        # Тест с слишком длинным названием
        invalid_data = {
            "name": "x" * 101,  # превышает максимум в 100 символов
            "description": "Chat with long name"
        }

        response = await client.post("/chats/", json=invalid_data, headers=user0_headers)
        assert response.status_code == 422

    async def test_chat_with_nonexistent_members(self, client: AsyncClient, auth_headers):
        """Тест создания чата с несуществующими участниками"""
        user0_headers = auth_headers["user0"]

        # Создаем чат с несуществующим участником
        chat_data = {
            "name": "Invalid Chat",
            "members": [str(uuid4())]  # несуществующий profile_id
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        assert response.status_code == 400

        error_detail = response.json()["error"]["message"]
        assert "members not found" in error_detail.lower()

    async def test_pagination_edge_cases(self, client: AsyncClient, auth_headers, test_users, session: AsyncSession):
        """Тест граничных случаев пагинации"""
        user0_headers = auth_headers["user0"]

        # Создаем чат
        chat_data = {
            "name": "Pagination Test Chat",
            "members": []
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        chat_id = response.json()["data"]["id"]

        # Добавляем 20 сообщений
        for i in range(20):
            message = MessageModel(
                chat_id=chat_id,
                sender_id=test_users[0]["profile_id"],
                text=f"Message {i+1:02d}",
                sent_at=f"2025-01-01T{i:02d}:00:00Z"
            )
            session.add(message)

        await session.commit()

        # Тест с limit больше количества сообщений
        response = await client.get(
            f"/chats/{chat_id}/history/?limit=50&offset=1",
            headers=user0_headers
        )
        assert response.status_code == 200
        history = response.json()["data"]
        assert history["totalCount"] == 20
        assert len(history["entities"]) == 20

        # Тест с offset больше количества сообщений
        response = await client.get(
            f"/chats/{chat_id}/history/?limit=10&offset=25",
            headers=user0_headers
        )
        assert response.status_code == 200
        history = response.json()["data"]
        assert history["totalCount"] == 20
        assert len(history["entities"]) == 0

    async def test_concurrent_chat_operations(self, client: AsyncClient, auth_headers, test_users):
        """Тест конкурентных операций с чатами"""
        user0_headers = auth_headers["user0"]
        user1_headers = auth_headers["user1"]

        # Создаем чат
        chat_data = {
            "name": "Concurrent Test Chat",
            "members": [test_users[1]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        chat_id = response.json()["data"]["id"]

        # Одновременные запросы на получение информации о чате
        tasks = []
        for _ in range(5):
            tasks.append(client.get(f"/chats/{chat_id}/", headers=user0_headers))
            tasks.append(client.get(f"/chats/{chat_id}/", headers=user1_headers))

        responses = await asyncio.gather(*tasks)

        # Все запросы должны быть успешными
        for response in responses:
            assert response.status_code == 200
            chat_data_response = response.json()["data"]
            assert chat_data_response["id"] == chat_id

    async def test_chat_response_format(self, client: AsyncClient, auth_headers, test_users):
        """Тест формата ответов API"""
        user0_headers = auth_headers["user0"]

        # Создаем чат
        chat_data = {
            "name": "Format Test Chat",
            "description": "Testing response format",
            "members": [test_users[1]["profile_id"]]
        }

        response = await client.post("/chats/", json=chat_data, headers=user0_headers)
        assert response.status_code == 200

        response_data = response.json()

        # Проверяем общий формат ответа
        assert "status" in response_data
        assert "data" in response_data
        assert response_data["status"] == "success"

        chat = response_data["data"]

        # Проверяем поля чата
        required_fields = ["id", "name", "description", "owner"]
        for field in required_fields:
            assert field in chat

        # Проверяем формат владельца
        owner = chat["owner"]
        owner_fields = ["id", "firstName", "lastName", "username"]
        for field in owner_fields:
            assert field in owner

        # Проверяем временные поля (camelCase)
        assert "createdAt" in chat
        assert "updatedAt" in chat

    async def test_unauthorized_access(self, client: AsyncClient):
        """Тест доступа без авторизации"""
        fake_chat_id = str(uuid4())

        # Все операции должны требовать авторизацию
        endpoints = [
            ("GET", "/chats/"),
            ("POST", "/chats/"),
            ("GET", f"/chats/{fake_chat_id}/"),
            ("PUT", f"/chats/{fake_chat_id}/"),
            ("DELETE", f"/chats/{fake_chat_id}/"),
            ("GET", f"/chats/{fake_chat_id}/history/"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={"name": "test"})
            elif method == "PUT":
                response = await client.put(endpoint, json={"name": "test"})
            elif method == "DELETE":
                response = await client.delete(endpoint)

            assert response.status_code == 401
