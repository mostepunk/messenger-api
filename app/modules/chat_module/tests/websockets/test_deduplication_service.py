import asyncio
from datetime import datetime
from uuid import uuid4

import pytest

from app.modules.chat_module.services.deduplication_service import (
    MessageDeduplicationService,
)


class TestMessageDeduplicationService:
    """Тесты для сервиса дедупликации сообщений"""

    @pytest.fixture
    def dedup_service(self):
        return MessageDeduplicationService()

    async def test_prevent_duplicate_message(self, dedup_service):
        """Тест предотвращения дубликата сообщения"""
        user_id = uuid4()
        chat_id = uuid4()
        text = "Тестовое сообщение"

        is_allowed, reason = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, text
        )
        assert is_allowed is True
        assert isinstance(reason, str)

        message_id = uuid4()
        await dedup_service.mark_message_sent(reason, message_id)

        is_allowed, reason = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, text
        )
        assert is_allowed is False
        assert "Wait" in reason

    async def test_different_users_same_message(self, dedup_service):
        """Тест: разные пользователи могут отправлять одинаковые сообщения"""
        user1_id = uuid4()
        user2_id = uuid4()
        chat_id = uuid4()
        text = "Одинаковое сообщение"

        is_allowed1, reason1 = await dedup_service.check_and_prevent_duplicate(
            user1_id, chat_id, text
        )
        assert is_allowed1 is True

        is_allowed2, reason2 = await dedup_service.check_and_prevent_duplicate(
            user2_id, chat_id, text
        )
        assert is_allowed2 is True
        assert reason1 != reason2  # Разные ключи для разных пользователей

    async def test_same_user_different_chats(self, dedup_service):
        """Тест: один пользователь может отправлять одинаковые сообщения в разные чаты"""
        user_id = uuid4()
        chat1_id = uuid4()
        chat2_id = uuid4()
        text = "Сообщение в разные чаты"

        is_allowed1, reason1 = await dedup_service.check_and_prevent_duplicate(
            user_id, chat1_id, text
        )
        assert is_allowed1 is True

        is_allowed2, reason2 = await dedup_service.check_and_prevent_duplicate(
            user_id, chat2_id, text
        )
        assert is_allowed2 is True
        assert reason1 != reason2

    async def test_cache_cleanup(self, dedup_service):
        """Тест очистки кэша устаревших сообщений"""
        old_key = "old_message_key"
        old_timestamp = datetime.now().timestamp() - 3600  # Час назад
        dedup_service._recent_messages[old_key] = (old_timestamp, uuid4())

        user_id = uuid4()
        chat_id = uuid4()

        await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, "новое сообщение"
        )

        assert old_key not in dedup_service._recent_messages

    async def test_empty_message_handling(self, dedup_service):
        """Тест обработки пустых сообщений"""
        user_id = uuid4()
        chat_id = uuid4()

        is_allowed1, reason1 = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, ""
        )
        assert is_allowed1 is False

        is_allowed2, reason2 = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, "   "
        )
        assert is_allowed2 is False

    async def test_whitespace_normalization(self, dedup_service):
        """Тест нормализации пробелов в сообщениях"""
        user_id = uuid4()
        chat_id = uuid4()

        text1 = "сообщение с пробелами"
        text2 = "  сообщение с пробелами  "
        text3 = "сообщение  с  пробелами"

        is_allowed1, reason1 = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, text1
        )
        assert is_allowed1 is True
        await dedup_service.mark_message_sent(reason1, uuid4())

        is_allowed2, reason2 = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, text2
        )
        assert is_allowed2 is False

    def test_get_stats(self, dedup_service):
        """Тест получения статистики сервиса"""
        dedup_service._recent_messages["key1"] = (datetime.now().timestamp(), uuid4())
        dedup_service._recent_messages["key2"] = (datetime.now().timestamp(), uuid4())

        stats = dedup_service.get_stats()

        assert "cached_messages" in stats
        assert "active_locks" in stats
        assert "cache_ttl" in stats
        assert "min_interval" in stats
        assert stats["cached_messages"] == 2

    async def test_concurrent_requests_same_message(self, dedup_service):
        """Тест конкурентных запросов с одинаковым сообщением"""

        user_id = uuid4()
        chat_id = uuid4()
        text = "Конкурентное сообщение"

        async def make_request():
            return await dedup_service.check_and_prevent_duplicate(
                user_id, chat_id, text
            )

        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        allowed_count = sum(1 for is_allowed, _ in results if is_allowed)
        # FAILS: 5 == 1
        assert allowed_count == 1

    async def test_message_key_generation(self, dedup_service):
        """Тест генерации ключей сообщений"""
        user_id = uuid4()
        chat_id = uuid4()
        text = "Тестовое сообщение"

        key1 = dedup_service._generate_message_key(user_id, chat_id, text)
        key2 = dedup_service._generate_message_key(user_id, chat_id, text)

        assert key1 == key2

        different_user_key = dedup_service._generate_message_key(uuid4(), chat_id, text)
        assert key1 != different_user_key

        different_chat_key = dedup_service._generate_message_key(user_id, uuid4(), text)
        assert key1 != different_chat_key
