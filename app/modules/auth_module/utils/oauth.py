from fastapi.security import OAuth2PasswordBearer

from app.settings import config

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=config.app.prefix + "/accounts/sign-in/swagger/",
)
