from uuid import UUID

from app.modules.base_module.schemas.base import BaseDB, BaseSchema


class AccountSessionBaseSchema(BaseSchema):
    refresh_token: str
    access_token: str
    fingerprint: str | None
    account_id: UUID


class AccountSessionDBSchema(AccountSessionBaseSchema, BaseDB):
    pass
