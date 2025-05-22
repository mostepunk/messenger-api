from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="auth_")

    email_pattern: str = r"^(?:[^@ \t\r\n]+)@(?:[^@ \t\r\n]+\.)+[^@ \t\r\n.]{2,}$"
    password_pattern: str = r"^(?=.*[a-zа-яА-Я])(?=.*[A-Zа-яА-Я]).{8,}$"
    email_strip_enabled: bool = True
    password_strip_enabled: bool = True
