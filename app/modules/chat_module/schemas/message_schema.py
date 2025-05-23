from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from app.modules.base_module.schemas.base import BaseDB, BaseSchema

if TYPE_CHECKING:
    from app.modules.chat_module.schemas.profile_schemas import ProfileSchema


class MessageSchema(BaseSchema):
    id: UUID
    text: str = Field(description="текст сообщения", example="hello")
    sender: "ProfileSchema"
    read_at: datetime | None
    sent_at: datetime


class MessageDBSchema(MessageSchema, BaseDB):
    pass


class MessageEntities(BaseSchema):
    total_count: int
    entities: list[MessageSchema]
