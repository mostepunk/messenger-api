import base64
import logging
import os
import tempfile
from typing import Any, Literal, Optional
from uuid import UUID

from fastapi_mail import MessageSchema, MessageType
from jinja2 import Template
from sqlalchemy import insert, select, update
from sqlalchemy.orm import joinedload

from app.adapters.clients.smtp import smtp_client
from app.adapters.db import ASYNC_SESSION
from app.modules.notify_module.db.models import (
    AttachmentModel,
    NotificationLogModel,
    TemplateModel,
)
from app.modules.notify_module.errors import NotificationTypeNotAllowed
from app.modules.notify_module.schemas.notify_schemas import (
    EmailRecipient,
)
from app.modules.notify_module.schemas.notify_schemas import (
    NotificationLogStatusEnum as NotifyStatus,
)
from app.modules.notify_module.schemas.notify_schemas import (
    NotificationTypeEnum,
    RecipientsSchema,
)


class NotificationService:
    def __init__(self):
        self.smtp_client = smtp_client

    async def notify(self, notification_data: dict[str, Any]):
        data = RecipientsSchema(**notification_data)

        if data.type == NotificationTypeEnum.email:
            return await self.send_email(data)

        raise NotificationTypeNotAllowed(f"Notification Type {data.type} Not Allowed.")

    async def send_email(self, recipient_data):
        template: TemplateModel = await self.get_template_by_code(recipient_data.code)

        for recipient in recipient_data.recipients:
            jinja_template = Template(template.body)
            body = jinja_template.render(**recipient.params)

            attachments = []
            temp_files = []

            temp_files, attachments = self._prepare_attachments(template.attachments)

            # from string import Template
            # tmp = Template(template.body)
            # body = tmp.substitute(**recipient.params)

            message = MessageSchema(
                subject=template.subject,
                recipients=recipient.emails,
                body=body,
                subtype=MessageType.html,
                attachments=attachments,
            )
            try:
                await self._send_email(message, recipient, template)
            finally:
                self._cleanup_temp_files(temp_files)

    async def _send_email(
        self, message: MessageSchema, recipient: EmailRecipient, template: TemplateModel
    ):
        # FIXME: эта библиотека делает рассылку не по каждому реципиенту,
        # как отдельное письмо, а в списке получателей отображаются все адреса.
        log_id = await self.write_log(
            status=NotifyStatus.prepared,
            columns={
                "template_id": template.id,
                "params": recipient.params,
                "recipients": {"emails": recipient.emails},
            },
        )
        try:
            await self.smtp_client.send_message(message)
        except Exception as err:
            logging.warning(
                f"Error on sending <{template.subject}> to {recipient.emails}. ERR: {err}"
            )
            await self.write_log(
                status=NotifyStatus.error,
                columns={"error_text": str(err)},
                log_id=log_id,
            )
            return

        logging.info(f"Email Subject: <{template.subject}> to {recipient.emails} sent.")
        await self.write_log(status=NotifyStatus.sent, log_id=log_id)

    async def get_template_by_code(self, code: str) -> TemplateModel:
        async with ASYNC_SESSION() as session:
            query = (
                select(TemplateModel)
                .where(TemplateModel.code == code)
                .options(joinedload(TemplateModel.attachments))
            )
            res = await session.scalar(query)
            return res

    async def write_log(
        self,
        status: str,
        columns: dict[
            Literal["template_id", "error_text", "params", "recipients"], Any
        ] = None,
        log_id: UUID = None,
    ):
        values = {"status": status}
        if columns:
            values.update(columns)

        if log_id:
            query = (
                update(NotificationLogModel)
                .where(NotificationLogModel.id == log_id)
                .values(values)
                .returning(NotificationLogModel.id)
            )
        else:
            query = (
                insert(NotificationLogModel)
                .values(values)
                .returning(NotificationLogModel.id)
            )
        async with ASYNC_SESSION() as session:
            res = await session.scalar(query)
            await session.commit()
            return res

    def _prepare_attachments(
        self, attachments: Optional[list[AttachmentModel]]
    ) -> tuple[list[str], list[dict]]:
        temp_files = []
        prepared = []

        if not attachments:
            return temp_files, prepared

        for a in attachments:
            temp_file_path = self._save_base64_to_temp_file(a.base64, a.filename)
            temp_files.append(temp_file_path)
            prepared.append(
                {
                    "file": temp_file_path,
                    "headers": {
                        "Content-ID": f"<{a.cid}>",
                        "Content-Disposition": f'inline; filename="{a.filename}"',
                    },
                    "mime_type": "image",
                    "mime_subtype": "svg",
                }
            )

        return temp_files, prepared

    @staticmethod
    def _save_base64_to_temp_file(base64_str: str, filename: str) -> str:
        decoded = base64.b64decode(base64_str)
        suffix = f"_{filename}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(decoded)
            return tmp.name

    @staticmethod
    def _cleanup_temp_files(paths: list[str]):
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
