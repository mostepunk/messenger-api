from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field, field_validator

from app.modules.base_module.schemas.base import BaseDB, BaseSchema

if TYPE_CHECKING:
    from app.modules.chat_module.schemas.profile_schemas import ProfileSchema


class ChatSchema(BaseSchema):
    id: UUID
    name: str = Field(description="название чата", example="chat name")
    description: str | None = Field(
        None, description="описание чата", example="chat description"
    )
    owner: "ProfileSchema" = Field(description="Владелец чата")


class DetailedChatSchema(ChatSchema):
    created_at: datetime
    updated_at: datetime
    members: list["ProfileSchema"] = Field(description="Участники чата")


class ChatDBSchema(ChatSchema, BaseDB):
    members: "list[ProfileSchema] | None" = Field(description="Участники чата")
    owner: "ProfileSchema" = Field(description="Владелец чата")


class CreateChatSchema(BaseSchema):
    name: str = Field(
        description="название чата",
        example="chat name",
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        None, description="описание чата", example="chat description", max_length=250
    )
    members: list[UUID] | None = Field(None, description="список участников")

    @field_validator("members")
    @classmethod
    def validate_members(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError("Список участников содержит дубликаты")
        return v


class UpdateChatSchema(CreateChatSchema):
    name: str | None = Field(None, description="название чата", example="chat name")
