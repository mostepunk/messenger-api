from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from app.modules.base_module.schemas.base import BaseDB, BaseSchema

if TYPE_CHECKING:
    from app.modules.chat_module.schemas.profile_schemas import ProfileSchema


class MessageSchema(BaseSchema):
    id: UUID
    text: str = Field(
        description="текст сообщения", example="hello", min_length=1, max_length=4000
    )
    sender: "ProfileSchema"
    read_at: datetime | None
    sent_at: datetime
    chat_id: UUID


class MessageDBSchema(MessageSchema, BaseDB):
    sender_id: UUID
    pass


class MessageEntities(BaseSchema):
    total_count: int
    entities: list[MessageSchema]
