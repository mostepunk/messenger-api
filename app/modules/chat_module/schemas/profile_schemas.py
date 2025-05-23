from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from app.modules.base_module.schemas.base import BaseDB, BaseSchema
from app.modules.base_module.schemas.customs import PhoneStr

if TYPE_CHECKING:
    from app.modules.chat_module.schemas.chat_schemas import ChatDBSchema


class BaseProfileSchema(BaseSchema):
    first_name: str = Field(example="Иван")
    last_name: str = Field(example="Иванов")
    middle_name: str = Field(example="Иванович")
    username: str = Field(example="povelitel_kisok777")


class ProfileSchema(BaseProfileSchema):
    id: UUID


class ProfilePDSchema(BaseSchema):
    phone: PhoneStr | None = Field(None, example="+7 (999) 333 44 55")


class ProfileDBSchema(ProfileSchema, BaseDB):
    pd: ProfilePDSchema | None = Field(None, description="персональные данные")
    chats: list["ChatDBSchema"] | None = Field(None, description="список чатов")
