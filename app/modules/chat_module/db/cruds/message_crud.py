import logging
from datetime import datetime
from operator import and_
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy import exists, func, literal, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import joinedload, selectinload

from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.chat_module.db.models.chat import (
    ChatUsersModel,
    MessageModel,
    MessageReadStatusModel,
)
from app.modules.chat_module.schemas.message_schema import (
    MessageDBSchema,
    MessageSchema,
)

if TYPE_CHECKING:
    from app.modules.chat_module.db.models.profile import ProfileModel


class MessageCRUD(BaseCRUD[MessageSchema, MessageDBSchema, MessageModel]):
    _in_schema = MessageSchema
    _out_schema = MessageDBSchema
    _table = MessageModel

    async def chat_history(
        self, chat_id: UUID, limit: int, offset: int
    ) -> tuple[int, list[MessageDBSchema]]:
        query = (
            select(self._table)
            .where(self._table.chat_id == chat_id)
            .options(
                joinedload(self._table.sender),
                joinedload(self._table.read_statuses),
                joinedload(self._table.readers),
            )
            .order_by(self._table.sent_at.desc())
        )
        total, items = await self.paginated_select(query, limit, offset)
        items = items.unique().all()
        validator = TypeAdapter(list[self._out_schema])
        validated_items = validator.validate_python(items)

        return total, list(reversed(validated_items))

    async def get_messages_by_ids(self, ids: list[UUID]) -> list[MessageDBSchema]:
        query = (
            select(self._table)
            .where(self._table.id.in_(ids))
            .options(
                joinedload(self._table.sender),
                selectinload(self._table.read_statuses),
                selectinload(self._table.readers),
            )
        )
        items = await self.session.scalars(query)
        items = items.unique().all()
        validator = TypeAdapter(list[self._out_schema])
        return validator.validate_python(items)

    async def mark_as_read(self, message_id: UUID) -> MessageDBSchema:
        """Простая отметка для 1-to-1 чатов."""
        query = (
            update(self._table)
            .where(self._table.id == message_id)
            .values(read_at=datetime.utcnow())
            .returning(self._table)
        )
        item = await self.session.scalar(query)
        await self.await_relations(item)
        return self._out_schema.model_validate(item)

    async def mark_messages_read_by_last_id(
        self, chat_id: UUID, profile_id: UUID, last_read_message_id: UUID
    ) -> list[UUID]:
        """
        Отметить все сообщения до указанного ID как прочитанные

        Args:
            chat_id: UUID чата
            profile_id: UUID пользователя
            last_read_message_id: UUID последнего прочитанного сообщения

        Returns:
            list[UUID]: Список ID сообщений, которые были отмечены как прочитанные
        """
        membership_check = select(ChatUsersModel).where(
            ChatUsersModel.chat_id == chat_id,
            ChatUsersModel.profile_id == profile_id,
        )
        membership = await self.session.scalar(membership_check)
        if not membership:
            logging.warning(f"User {profile_id} is not member of chat {chat_id}")
            return []

        unread_messages_cte = (
            select(
                self._table.id.label("message_id"),
                literal(profile_id).label("profile_id"),
                literal(datetime.utcnow()).label("read_at"),
            )
            .select_from(self._table)
            .outerjoin(
                MessageReadStatusModel,
                and_(
                    MessageReadStatusModel.message_id == self._table.id,
                    MessageReadStatusModel.profile_id == profile_id,
                ),
            )
            .join(
                ChatUsersModel,
                and_(
                    ChatUsersModel.chat_id == chat_id,
                    ChatUsersModel.profile_id == profile_id,
                ),
            )
            .where(
                self._table.chat_id == chat_id,
                self._table.sender_id != profile_id,
                self._table.sent_at
                <= (
                    select(self._table.sent_at)
                    .where(self._table.id == last_read_message_id)
                    .scalar_subquery()
                ),
                MessageReadStatusModel.message_id.is_(None),  # Еще не прочитано
                # Проверка существования сообщения встроена в условие
                exists().where(
                    and_(
                        self._table.id == last_read_message_id,
                        self._table.chat_id == chat_id,
                    )
                ),
            )
            .cte("unread_messages")
        )

        unread_messages_query = select(unread_messages_cte.c.message_id)
        unread_message_ids = list(await self.session.scalars(unread_messages_query))
        if not unread_message_ids:
            return []

        read_statuses_data = [
            {
                "message_id": message_id,
                "profile_id": profile_id,
                "read_at": datetime.utcnow(),
            }
            for message_id in unread_message_ids
        ]

        stmt = pg_insert(MessageReadStatusModel).values(read_statuses_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["message_id", "profile_id"])
        await self.session.execute(stmt)
        logging.debug(f"Marked {len(unread_message_ids)} messages as read")

        return unread_message_ids

    async def mark_as_read_by_profile(self, message_id: UUID, profile_id: UUID) -> bool:
        """
        Args:
            message_id: UUID сообщения
            profile_id: UUID пользователя

        Returns:
            bool: True если сообщение было отмечено, False если уже было прочитано
        """
        try:
            stmt = pg_insert(MessageReadStatusModel).values(
                {
                    "message_id": message_id,
                    "profile_id": profile_id,
                    "read_at": datetime.utcnow(),
                }
            )
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["message_id", "profile_id"]
            )
            result = await self.session.execute(stmt)
            # Если rowcount > 0, значит запись была вставлена
            was_inserted = result.rowcount > 0

            if was_inserted:
                logging.info(
                    f"Message {message_id} marked as read by profile {profile_id}"
                )

            return was_inserted

        except Exception as e:
            logging.error(f"Error marking message as read: {e}")
            return False

    async def get_unread_count_for_user(self, chat_id: UUID, profile_id: UUID) -> int:
        """Получить количество непрочитанных сообщений для пользователя в чате."""
        read_messages_subquery = select(MessageReadStatusModel.message_id).where(
            MessageReadStatusModel.profile_id == profile_id
        )

        unread_query = select(func.count(self._table.id)).where(
            self._table.chat_id == chat_id,
            self._table.sender_id != profile_id,
            self._table.id.notin_(read_messages_subquery),
        )

        result = await self.session.scalar(unread_query)
        return result or 0
