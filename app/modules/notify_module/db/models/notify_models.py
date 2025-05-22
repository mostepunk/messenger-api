from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey as FK
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.base_module.db.models.base import Base
from app.modules.notify_module.schemas.notify_schemas import NotificationTypeEnum


class TemplateModel(Base):
    __tablename__ = "notification_template"

    type: Mapped[str] = mapped_column(String(10), default=NotificationTypeEnum.email)
    subject: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text)
    code: Mapped[str] = mapped_column(String(50), unique=True)

    attachments: Mapped[Optional[list["AttachmentModel"]]] = relationship()


class AttachmentModel(Base):
    __tablename__ = "notification_attachment"

    base64: Mapped[str] = mapped_column(Text)
    template_id: Mapped[UUID] = mapped_column(FK("notification_template.id"))
    filename: Mapped[str] = mapped_column(String(100))
    cid: Mapped[str] = mapped_column(String(100))


class NotificationLogModel(Base):
    __tablename__ = "notification_log"

    template_id: Mapped[UUID] = mapped_column(FK("notification_template.id"))
    params: Mapped[dict] = mapped_column(JSONB)
    recipients: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50))
    error_text: Mapped[str | None] = mapped_column(String(255))
