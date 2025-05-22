from enum import Enum, unique

from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict


@unique
class ApiMode(str, Enum):
    prod: str = "PROD"
    dev: str = "DEV"
    local: str = "LOCAL"


class BaseSettings(_BaseSettings):
    environment: ApiMode = ApiMode.prod

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
