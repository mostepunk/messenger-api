from pydantic_settings import SettingsConfigDict

from .base import ApiMode, BaseSettings
from app.settings.base import BaseSettings


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="jwt_")

    secret_key: str = (
        "06fc53c2b88753232b1060b644f05e2165d364977d226775616ea6330c0189b96c"
    )
    alg: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 60
    confirmation_token_expire_days: int = 2

    @property
    def token_expire(self) -> int:
        if self.environment == ApiMode.local:
            return 24 * 60  # 24 hours

        return self.access_token_expire_minutes
