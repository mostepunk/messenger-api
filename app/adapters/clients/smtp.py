from fastapi_mail import ConnectionConfig, FastMail

from app.settings import config
from app.settings.base import ApiMode

if config.environment == ApiMode.local and "gmail" in config.smtp.server:
    smtp_client = FastMail(
        ConnectionConfig(
            MAIL_SERVER=config.smtp.server,
            MAIL_PORT=config.smtp.port,
            MAIL_USERNAME=config.smtp.username,
            MAIL_PASSWORD=config.smtp.password,
            MAIL_FROM_NAME=config.smtp.from_name,
            MAIL_FROM=config.smtp.from_email,
            TIMEOUT=config.smtp.timeout,
            # Do not change
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False,
        )
    )
else:
    smtp_client = FastMail(
        ConnectionConfig(
            MAIL_SERVER=config.smtp.server,
            MAIL_PORT=config.smtp.port,
            MAIL_USERNAME=config.smtp.username,
            MAIL_PASSWORD=config.smtp.password,
            MAIL_FROM_NAME=config.smtp.from_name,
            MAIL_FROM=config.smtp.from_email,
            TIMEOUT=config.smtp.timeout,
            # Do not change
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False,
        )
    )
