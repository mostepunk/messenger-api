from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.chat_module.db.models.chat import ChatModel
from app.modules.chat_module.schemas.chat_schemas import ChatDBSchema, ChatSchema

if TYPE_CHECKING:
    from app.modules.chat_module.db.models.profile import ProfileModel


class ChatCRUD(BaseCRUD[ChatSchema, ChatDBSchema, ChatModel]):
    _in_schema = ChatSchema
    _out_schema = ChatDBSchema
    _table = ChatModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_members(self, chat_id: UUID, members: list["ProfileModel"]):
        chat = await self.get_by_id(chat_id, return_raw=True)
        chat.members = members

    async def full_chat_info(self, chat_id: UUID):
        query = (
            select(self._table)
            .where(self._table.id == chat_id)
            .options(
                joinedload(self._table.members),
                joinedload(self._table.owner),
            )
        )
        item = await self.session.scalar(query)
        return item
