import asyncio
import hashlib
import logging
import time
from collections import defaultdict
from typing import Dict
from uuid import UUID

from app.settings import config


class MessageDeduplicationService:
    """Сервис для предотвращения дублирования сообщений при параллельной отправке"""

    def __init__(self):
        self._user_chat_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        # Кэш отправленных сообщений: ключ -> (timestamp, message_id)
        self._recent_messages: Dict[str, tuple[float, UUID]] = {}
        self._cache_ttl_seconds = config.chat.cache_ttl_seconds
        self._min_message_interval = config.chat.min_message_interval

    async def check_and_prevent_duplicate(
        self, user_id: UUID, chat_id: UUID, text: str
    ) -> tuple[bool, str]:
        """
        Проверяет и предотвращает дублирование сообщения

        Returns:
            tuple: (is_allowed, reason) - разрешено ли отправлять сообщение и причина
        """
        lock_key = self._get_user_chat_lock_key(user_id, chat_id)
        message_key = self._generate_message_key(user_id, chat_id, text)

        async with self._user_chat_locks[lock_key]:
            logging.debug(f"Acquired lock for user {user_id} in chat {chat_id}")
            logging.debug(
                f"Message key in recent: {message_key in self._recent_messages}"
            )
            current_time = time.time()

            if message_key in self._recent_messages:
                last_time, last_message_id = self._recent_messages[message_key]
                time_diff = current_time - last_time
                logging.info(f"Last message ID: {last_message_id} at {last_time}")
                logging.info(f"Time diff: {time_diff} seconds")

                if time_diff < self._min_message_interval:
                    return (
                        False,
                        f"Too frequent. Wait {self._min_message_interval - time_diff:.1f}s",
                    )

                del self._recent_messages[message_key]

            await self._cleanup_expired_messages()
            return True, message_key

    def _get_user_chat_lock_key(self, user_id: UUID, chat_id: UUID) -> str:
        """Генерирует ключ для блокировки пользователя в чате"""
        return f"{user_id}:{chat_id}"

    def _generate_message_key(self, user_id: UUID, chat_id: UUID, text: str) -> str:
        """Генерирует ключ для идентификации сообщения"""
        content = f"{user_id}:{chat_id}:{text.strip()}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def mark_message_sent(self, message_key: str, message_id: UUID):
        """Отмечает сообщение как отправленное

        отмечено в асинхронном режиме, потому что этот сервис мокается через AsyncMock
        и пытается запустить его в асинхронном режиме
        """
        self._recent_messages[message_key] = (time.time(), message_id)

    async def _cleanup_expired_messages(self):
        """Очищает устаревшие записи из кэша"""
        current_time = time.time()
        expired_keys = [
            key
            for key, (timestamp, _) in self._recent_messages.items()
            if current_time - timestamp > self._cache_ttl_seconds
        ]

        for key in expired_keys:
            del self._recent_messages[key]
        logging.debug(f"Removed {len(expired_keys)} expired messages")

    def get_stats(self) -> dict:
        """Возвращает статистику сервиса"""
        return {
            "cached_messages": len(self._recent_messages),
            "active_locks": len(self._user_chat_locks),
            "cache_ttl": self._cache_ttl_seconds,
            "min_interval": self._min_message_interval,
        }


deduplication_service = MessageDeduplicationService()
