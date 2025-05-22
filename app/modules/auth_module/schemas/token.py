from datetime import datetime
from enum import Enum
from uuid import UUID

from app.modules.base_module.schemas.base import BaseSchema
from app.modules.base_module.schemas.customs import EmailStr


class TokenTypeEnum(str, Enum):
    access_type: str = "access"
    refresh_type: str = "refresh"
    confirmation_type: str = "confirmation"


class Token(BaseSchema):
    user_id: UUID
    email: EmailStr
    exp: datetime | None = None
    token_type: TokenTypeEnum


class AuthTokens(BaseSchema):
    access_token: str | None = None
