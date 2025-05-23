from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey as FK
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.base_module.db.models.base import Base

if TYPE_CHECKING:
    from app.modules.chat_module.db.models.profile import ProfileModel


class ChatModel(Base):
    __tablename__ = "chat"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(250))
    owner_id: Mapped[UUID] = mapped_column(FK("profile.id", ondelete="CASCADE"))

    messages: Mapped[list["MessageModel"] | None] = relationship(lazy="selectin")
    members: Mapped[list["ProfileModel"]] = relationship(
        secondary="chat_user",
        back_populates="chats",
        lazy="selectin",
    )
    owner: Mapped["ProfileModel"] = relationship()


class MessageModel(Base):
    __tablename__ = "message"

    chat_id: Mapped[UUID | None] = mapped_column(FK("chat.id", ondelete="CASCADE"))
    text: Mapped[str]
    sender_id: Mapped[UUID | None] = mapped_column(
        FK("profile.id", ondelete="SET NULL")
    )
    read_at: Mapped[datetime | None]
    sent_at: Mapped[datetime | None]

    sender: Mapped["ProfileModel | None"] = relationship()


class ChatUsersModel(Base):
    __tablename__ = "chat_user"

    chat_id: Mapped[UUID] = mapped_column(FK("chat.id", ondelete="CASCADE"))
    profile_id: Mapped[UUID] = mapped_column(FK("profile.id", ondelete="CASCADE"))
