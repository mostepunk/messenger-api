from pydantic import EmailStr

from app.modules.base_module.schemas.base import BaseSchema, StrEnum


class NotificationTypeEnum(StrEnum):
    sms: str = "sms", "смс"
    email: str = "email", "электронная почта"
    push: str = "push", "пуш уведомление"


class NotificationLogStatusEnum(StrEnum):
    prepared: str = "prepared", "подготовлено"
    sent: str = "sent", "отправлено"
    error: str = "error", "ошибка отправки"


class BaseRecipient(BaseSchema):
    params: dict


class EmailRecipient(BaseRecipient):
    emails: list[EmailStr]


class SMSRecipient(BaseRecipient):
    phone: str


class RecipientsSchema(BaseSchema):
    type: NotificationTypeEnum = NotificationTypeEnum.email
    code: str
    recipients: list[EmailRecipient | SMSRecipient]
