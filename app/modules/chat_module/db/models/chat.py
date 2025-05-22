from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey as FK
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.base_module.db.models.base import Base


class ChatModel(Base):
    __tablename__ = "chat"

    descritpion: Mapped[str | None] = mapped_column(String(250))

    messages: Mapped[list["MessageModel"] | None] = relationship(lazy="selectin")


class MessageModel(Base):
    __tablename__ = "message"

    chat_id: Mapped[UUID | None] = mapped_column(FK("chat.id", ondelete="CASCADE"))
    text: Mapped[str]
    sender_id: Mapped[UUID | None] = mapped_column(
        FK("profile.id", ondelete="SET NULL")
    )
    read_at: Mapped[datetime | None]
    sent_at: Mapped[datetime | None]


class ChatUsersModel(Base):
    __tablename__ = "chat_user"

    chat_id: Mapped[UUID] = mapped_column(FK("chat.id", ondelete="CASCADE"))
    profile_id: Mapped[UUID] = mapped_column(FK("profile.id", ondelete="CASCADE"))
