import os

from pydantic_settings import SettingsConfigDict

from app.settings.base import BaseSettings


class DBSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="pg_server_")

    login: str
    passwd: str
    address: str
    port: str
    db: str
    db_schema: str = "public"
    dialect: str = "postgresql"
    test_prefix: str = "_testing"
    echo: bool = False
    chunk_size: int = 1000

    @property
    def db_name(self):
        return (
            f"{self.db}_{self.test_prefix}"
            if os.environ.get("TESTING") == "True"
            else self.db
        )

    @property
    def db_uri(self):
        return (
            f"{self.login}:{self.passwd}@{self.address}:" f"{self.port}/{self.db_name}"
        )

    @property
    def async_db_uri(self):
        return f"{self.dialect}+psycopg://{self.db_uri}"

    @property
    def sync_db_uri(self):
        return f"{self.dialect}+psycopg2://{self.db_uri}"

    @property
    def alembic_db_uri(self):
        return f"{self.dialect}+asyncpg://{self.db_uri}"

    @property
    def dsn_no_driver(self) -> str:
        """Полученние dsn без определенного драйвера БД.

        Returns:
            Собранный dsn
        """
        return f"{self.dialect}://{self.db_uri}"
