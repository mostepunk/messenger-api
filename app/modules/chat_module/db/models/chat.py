from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey as FK
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.base_module.db.models.base import Base

if TYPE_CHECKING:
    from app.modules.chat_module.db.models import ProfileModel


class ChatModel(Base):
    __tablename__ = "chat"
    __table_args__ = {"extend_existing": True}

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(250))
    owner_id: Mapped[UUID] = mapped_column(FK("profile.id", ondelete="CASCADE"))

    members: Mapped[list["app.modules.chat_module.db.models.profile.ProfileModel"]] = (
        relationship(
            "app.modules.chat_module.db.models.profile.ProfileModel",
            secondary="chat_user",
            viewonly=True,
        )
    )
    owner: Mapped["ProfileModel"] = relationship(
        "app.modules.chat_module.db.models.profile.ProfileModel"
    )


class ChatUsersModel(Base):
    __tablename__ = "chat_user"
    __table_args__ = {"extend_existing": True}

    chat_id: Mapped[UUID] = mapped_column(FK("chat.id", ondelete="CASCADE"), index=True)
    profile_id: Mapped[UUID] = mapped_column(
        FK("profile.id", ondelete="CASCADE"), index=True
    )


class MessageReadStatusModel(Base):
    __tablename__ = "message_read_status"

    message_id: Mapped[UUID] = mapped_column(
        FK("message.id", ondelete="CASCADE"), index=True
    )
    profile_id: Mapped[UUID] = mapped_column(
        FK("profile.id", ondelete="CASCADE"), index=True
    )
    read_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("message_id", "profile_id", name="unique_message_user_read"),
        {"extend_existing": True},
    )


class MessageModel(Base):
    __tablename__ = "message"
    __table_args__ = {"extend_existing": True}

    chat_id: Mapped[UUID | None] = mapped_column(
        FK("chat.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str]
    sender_id: Mapped[UUID | None] = mapped_column(
        FK("profile.id", ondelete="SET NULL"), index=True
    )
    # подойдет, только для чатов 1to1
    read_at: Mapped[datetime | None]
    sent_at: Mapped[datetime | None] = mapped_column(index=True)

    sender: Mapped["app.modules.chat_module.db.models.profile.ProfileModel | None"] = (
        relationship()
    )
    read_statuses: Mapped[list[MessageReadStatusModel]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    readers: Mapped[
        list["app.modules.chat_module.db.models.profile.ProfileModel"] | None
    ] = relationship(
        secondary="message_read_status",
        lazy="selectin",
        overlaps="read_statuses",
    )

    def is_read_by(self, profile_id: UUID) -> bool:
        """Проверить, прочитано ли сообщение конкретным пользователем"""
        return any(status.profile_id == profile_id for status in self.read_statuses)

    @property
    def readers_ids(self) -> list[UUID]:
        """Получить список пользователей, которые прочитали сообщение"""
        return [status.profile_id for status in self.read_statuses]

    def get_read_at_for_user(self, profile_id: UUID) -> datetime | None:
        """Получить время прочтения для конкретного пользователя"""
        for status in self.read_statuses:
            if status.profile_id == profile_id:
                return status.read_at
        return None
