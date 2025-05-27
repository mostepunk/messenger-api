from uuid import UUID, uuid4

from pydantic import Field, model_validator

from app.modules.auth_module.dependencies.token import (
    create_access_token,
    create_confirmation_token,
    create_refresh_token,
)
from app.modules.auth_module.schemas.account_session import AccountSessionBaseSchema
from app.modules.auth_module.schemas.token import TokenTypeEnum
from app.modules.auth_module.utils.errors import (
    CredentialsError,
)
from app.modules.base_module.schemas.base import BaseDB, BaseSchema
from app.modules.base_module.schemas.customs import (
    EmailStr,
    PasswordStr,
)


class AccountBase(BaseSchema):
    email: EmailStr = Field(example="user@example.com")


class AccountSchema(AccountBase):
    id: UUID


class AccountDBSchema(AccountBase, BaseDB):
    confirmation_token: str | None = None
    is_confirmed: bool
    password: str
    sessions: list[AccountSessionBaseSchema] | None = None

    @property
    def confirm_token(self):
        return create_confirmation_token(self.id, self.email)

    @property
    def access_token(self):
        return create_access_token(self.id, self.email)

    @property
    def refresh_token(self):
        return create_refresh_token(self.id, self.email)

    @property
    def can_account_create_session(self) -> bool:
        """Проверить, может ли пользователь создать еще одну сессию"""
        return True

    def create_session(self, fingerprint: str):
        return AccountSessionBaseSchema(
            refresh_token=self.refresh_token,
            access_token=self.access_token,
            account_id=self.id,
            fingerprint=fingerprint,
        )

    def delete_session(
        self, session: AccountSessionBaseSchema
    ) -> AccountSessionBaseSchema | None:
        if session in self.sessions:
            return self.sessions.pop(self.sessions.index(session), None)
        return None

    def get_session(
        self, token: str, token_attr: TokenTypeEnum | str
    ) -> AccountSessionBaseSchema | None:
        return next(
            (
                session
                for session in self.sessions
                if getattr(session, token_attr) == token
            ),
            None,
        )


class AccountRegisterSchema(AccountBase):
    password: PasswordStr = Field(example="qwerty123")


class AccountSignInSchema(AccountBase):
    password: str = Field(example="qwerty123")
    fingerprint: str | None = Field(
        None,
        example=str(uuid4()),
        description="отпечаток браузера",
    )


class EmailExistsSchema(BaseSchema):
    exists: bool


class NewPasswordsSchema(BaseSchema):
    password: PasswordStr = Field(example="qwerty123")


class AccountRefreshTokenSchema(BaseSchema):
    fingerprint: str | None


class AccountPasswordResetSchema(AccountBase):
    email: EmailStr = Field(example="user@example.com")


class AccountConfirmEmailSchema(BaseSchema):
    confirmation_token: str
    fingerprint: str

    @model_validator(mode="before")
    @classmethod
    def validate_confirmation_token(cls, values: dict) -> dict:
        if not values.get("confirmationToken") or not values.get("fingerprint"):
            raise CredentialsError
        return values
