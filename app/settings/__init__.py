from .app_settings import AppSettings
from .auth_settings import AuthSettings
from .base import ApiMode, BaseSettings
from .db_settings import DBSettings
from .jwt_settings import JWTSettings
from .log import LogSettings
from .modules_settings import ModuleSettings
from .smtp_settings import SMTPSettings


class Config(BaseSettings):

    app: AppSettings = AppSettings()
    log: LogSettings = LogSettings()
    db: DBSettings = DBSettings()
    modules: ModuleSettings = ModuleSettings()
    jwt: JWTSettings = JWTSettings()
    smtp: SMTPSettings = SMTPSettings()
    auth: AuthSettings = AuthSettings()


config = Config()
