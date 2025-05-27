import logging
from enum import Enum, unique

from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings


@unique
class LogLevel(str, Enum):
    notset: str = "NOTSET"
    debug: str = "DEBUG"
    info: str = "INFO"
    warning: str = "WARNING"
    error: str = "ERROR"
    critical: str = "CRITICAL"


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="log_")

    enable: bool = True
    level: LogLevel = LogLevel.info
    format: str = (
        "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d | %(levelname)-7s | %(message)s"
    )

    access_log_path: str = "./logs/access.log"
    asgi_log_path: str = "./logs/asgi.log"
    write_to_file: bool = False

    @property
    def logging_level(self):
        return getattr(logging, self.level)
