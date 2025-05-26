from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings


class ChatSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="chat_")

    cache_ttl_seconds: int = 60
    min_message_interval: float = 1.0
