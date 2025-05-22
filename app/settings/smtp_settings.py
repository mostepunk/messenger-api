from pydantic import EmailStr, SecretStr
from pydantic_settings import SettingsConfigDict

from .base import BaseSettings
from app.settings.base import BaseSettings


class SMTPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="mail_")

    server: str
    port: int = 465
    username: str
    password: SecretStr
    from_name: str = "Messenger"
    from_email: EmailStr
    timeout: int = 10
