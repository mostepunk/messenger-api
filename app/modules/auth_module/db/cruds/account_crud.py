# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs.awaitable_attrs

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.auth_module.db.models import AccountModel
from app.modules.auth_module.schemas.account import AccountDBSchema, AccountSchema
from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.base_module.db.errors import (
    ItemNotFoundError,
)


class AccountCRUD(BaseCRUD[AccountSchema, AccountDBSchema, AccountModel]):
    _in_schema = AccountSchema
    _out_schema = AccountDBSchema
    _table = AccountModel

    def __init__(self, session: AsyncSession):
        self.session = session
        self.select = select(self._table)

    async def find_by_email(
        self, email: str, raise_err: bool = True
    ) -> AccountDBSchema | None:
        query = (
            select(self._table)
            .where(self._table.email == email)
            .options(self.joinedload_profile)
        )

        res = await self.session.scalar(query)
        if not res:
            if raise_err:
                raise ItemNotFoundError(f"Account by {email} not found")
            return None

        return self._out_schema.model_validate(res)

    async def get_by_id(self, item_uuid: UUID) -> AccountDBSchema:
        """Получение записи по уникальному идентификатору"""

        query = (
            select(self._table)
            .where(self._table.id == item_uuid)
            .options(self.joinedload_profile)
        )
        item = await self.session.scalar(query)
        await self.await_relations(item)
        if not item:
            raise ItemNotFoundError(f"Item {item_uuid} not found")
        return self._out_schema.model_validate(item)

    @property
    def joinedload_profile(self):
        # FIXME: эти импорты тут специально лежат, чтобы не было цикличных импортов
        from app.modules.chat_module.db.models.profile import ProfileModel
        from app.modules.chat_module.db.models.chat import ChatModel

        return joinedload(self._table.profile).options(
                    joinedload(ProfileModel.pd),
                    joinedload(ProfileModel.chats).options(
                        joinedload(ChatModel.members),
                        joinedload(ChatModel.owner)
                    ),
                )
