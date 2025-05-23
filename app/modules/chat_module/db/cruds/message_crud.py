from uuid import UUID

from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.chat_module.db.models.chat import MessageModel
from app.modules.chat_module.schemas.message_schema import (
    MessageDBSchema,
    MessageSchema,
)


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
            .options(joinedload(self._table.sender))
            .order_by(self._table.sent_at.desc())
        )
        total, items = await self.paginated_select(query, limit, offset)
        validator = TypeAdapter(list[self._out_schema])
        validated_items = validator.validate_python(items)

        return total, list(reversed(validated_items))
