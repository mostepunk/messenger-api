from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey as FK
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.base_module.db.models.base import Base

if TYPE_CHECKING:
    from app.modules.chat_module.db.models.chat import ChatModel


class ProfilePersonalDataModel(Base):
    __tablename__ = "profile_personal_data"
    __table_args__ = {"extend_existing": True}

    profile_id: Mapped[UUID] = mapped_column(
        FK("profile.id", ondelete="CASCADE"), unique=True
    )
    phone: Mapped[str | None] = mapped_column(String(12), unique=True)


class ProfileModel(Base):
    __tablename__ = "profile"
    __table_args__ = {"extend_existing": True}

    last_name: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(100))
    middle_name: Mapped[str | None] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(String(100), unique=True)

    pd: Mapped[ProfilePersonalDataModel] = relationship()
    chats: Mapped[list["app.modules.chat_module.db.models.chat.ChatModel"] | None] = (
        relationship(
            secondary="chat_user",
            lazy="selectin",
            back_populates="members",
        )
    )
