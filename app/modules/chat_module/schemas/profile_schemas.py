from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from app.modules.base_module.schemas.base import BaseDB, BaseSchema
from app.modules.base_module.schemas.customs import PhoneStr

if TYPE_CHECKING:
    from app.modules.chat_module.schemas.chat_schemas import ChatDBSchema


class BaseProfileSchema(BaseSchema):
    first_name: str | None = Field(None, example="Иван", min_length=1, max_length=100)

    last_name: str | None = Field(None, example="Иванов", min_length=1, max_length=100)
    middle_name: str | None = Field(None, example="Иванович", max_length=100)
    username: str | None = Field(
        None, example="povelitel_kisok777", min_length=3, max_length=50
    )


class ProfileSchema(BaseProfileSchema):
    id: UUID


class ProfilePDSchema(BaseSchema):
    phone: PhoneStr | None = Field(None, example="+7 (999) 333 44 55")


class ProfileDBSchema(ProfileSchema, BaseDB):
    pd: ProfilePDSchema | None = Field(None, description="персональные данные")
    chats: list["ChatDBSchema"] | None = Field(None, description="список чатов")

    def find_chat(self, chat_id: UUID) -> "ChatDBSchema | None":
        return next((chat for chat in self.chats if chat.id == chat_id), None)

    @property
    def chat_ids(self) -> list[UUID]:
        return [chat.id for chat in self.chats]

    def is_memeber_of_chat(self, chat_id: UUID) -> bool:
        return chat_id in self.chat_ids

    def is_owner_of_chat(self, chat_id: UUID) -> bool:
        chat = self.find_chat(chat_id)
        if chat is None:
            return False

        return chat.owner.id == self.id
