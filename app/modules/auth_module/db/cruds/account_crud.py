# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs.awaitable_attrs

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        query = select(self._table).where(self._table.email == email)
        res = await self.session.scalar(query)
        if not res:
            if raise_err:
                raise ItemNotFoundError(f"Account by {email} not found")
            return None

        return self._out_schema.model_validate(res)
