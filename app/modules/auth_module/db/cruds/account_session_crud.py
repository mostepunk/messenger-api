from uuid import UUID

from sqlalchemy import delete, exists, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth_module.db.models.account import AccountSessionModel
from app.modules.auth_module.schemas.account_session import (
    AccountSessionBaseSchema,
    AccountSessionDBSchema,
)
from app.modules.base_module.db.cruds.base_crud import BaseCRUD


class AccountSessionCRUD(
    BaseCRUD[AccountSessionBaseSchema, AccountSessionDBSchema, AccountSessionModel]
):
    _in_schema = AccountSessionBaseSchema
    _out_schema = AccountSessionDBSchema
    _table = AccountSessionModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_refresh_token(
        self, refresh_token: str, account_id: UUID, values: dict
    ):
        query = (
            update(self._table)
            .where(
                self._table.refresh_token == refresh_token,
                self._table.account_id == account_id,
            )
            .values(values)
            .returning(self._table)
        )
        account_session = await self.session.scalar(query)
        return account_session

    async def delete_session(self, refresh_token: str):
        query = (
            delete(self._table)
            .where(self._table.refresh_token == refresh_token)
            .returning(self._table)
        )
        return await self.session.scalar(query)

    async def access_token_exists(self, access_token: str):
        result = await self.session.execute(
            select(
                exists().where(
                    or_(
                        self._table.access_token == access_token,
                        self._table.refresh_token == access_token,
                    )
                )
            )
        )
        exists_result = result.scalar()
        return exists_result
