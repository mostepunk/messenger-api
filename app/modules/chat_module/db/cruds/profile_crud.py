from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.base_module.db.errors import (
    ItemNotFoundError,
)
from app.modules.chat_module.db.models.chat import ChatModel
from app.modules.chat_module.db.models.profile import ProfileModel
from app.modules.chat_module.schemas.profile_schemas import (
    ProfileDBSchema,
    ProfileSchema,
)


class ProfileCRUD(BaseCRUD[ProfileSchema, ProfileDBSchema, ProfileModel]):
    _in_schema = ProfileSchema
    _out_schema = ProfileDBSchema
    _table = ProfileModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile_by_account_id(self, account_id: UUID):
        query = (
            select(self._table)
            .where(self._table.account_id == account_id)
            .options(
                joinedload(self._table.pd),
                joinedload(self._table.chats).options(
                    joinedload(ChatModel.members),
                    joinedload(ChatModel.owner),
                ),
            )
        )
        item = await self.session.scalar(query)
        # await self.await_relations(item)
        if not item:
            raise ItemNotFoundError(f"Profile for account {account_id} not found")
        return self._out_schema.model_validate(item)
