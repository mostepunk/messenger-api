from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer
from jwt import DecodeError
from pydantic import ValidationError

from .errors import (
    BaseTokenException,
    InvalidTokenError,
    InvalidTokenTypeError,
    TokenDecodeError,
    TokenExpiredError,
)
from app.adapters.db import ASYNC_SESSION
from app.modules.auth_module.db.cruds.account_session_crud import AccountSessionCRUD
from app.modules.auth_module.schemas.account import AccountSchema
from app.modules.auth_module.schemas.token import Token, TokenTypeEnum
from app.modules.auth_module.utils.oauth import oauth2_scheme
from app.settings import config

security = HTTPBearer()


def token_expired(input_datetime: str | datetime) -> bool:
    if isinstance(input_datetime, str):
        input_datetime = datetime.fromisoformat(input_datetime)
    if input_datetime < datetime.now():
        return True
    return False


async def decode_token(token: str, check_in_db: bool = True) -> Token:
    """
    - Проверить записан ли токен в БД.
    - Извлечь данные из токена
    """
    if check_in_db:
        async with ASYNC_SESSION() as session:
            crud = AccountSessionCRUD(session)
            exists = await crud.access_token_exists(token)
        if not exists:
            logging.warning(f"Token not registered in DB")
            raise InvalidTokenError

    try:
        raw_token = jwt.decode(
            token,
            algorithms=config.jwt.alg,
            key=config.jwt.secret_key,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iss": False,
            },
        )
        return Token(**raw_token)
    except DecodeError as err:
        logging.warning(f"Token DecodeError: {err}")
        raise TokenDecodeError("Invalid JWT token") from err

    except ValidationError as err:
        logging.warning(f"Invalid token schema inside token dict: {err}")
        raise InvalidTokenError


async def decode_token_and_check_exp(token: str) -> Token:
    decoded = await decode_token(token, check_in_db=False)

    if token_expired(decoded.exp):
        raise TokenExpiredError
    return decoded


async def get_account_from_token(
    raw_token: Annotated[str, Depends(oauth2_scheme)]
) -> AccountSchema:
    """Получение пользователя из токена"""
    try:
        token: Token = await decode_token(raw_token)
        account = AccountSchema(id=token.user_id, email=token.email)
    except ValidationError as err:
        logging.warning(f"Invalid token schema inside token dict: {err}")
        raise InvalidTokenError
    except Exception as err:
        logging.warning(f"Exception in get_account_from_token: {err}")
        raise BaseTokenException

    else:
        if token_expired(token.exp):
            raise TokenExpiredError

        if token.token_type == TokenTypeEnum.refresh_type:
            raise InvalidTokenTypeError
        return account


async def check_refresh_token(raw_token: str):
    if not raw_token:
        logging.warning("Token is empty")
        raise InvalidTokenError
    try:
        token: Token = await decode_token(raw_token)
    except ValidationError as err:
        logging.warning(f"Invalid schema in refresh_token: {err}")
        raise InvalidTokenError
    except Exception as err:
        logging.warning(f"BaseTokenException: {err}")
        raise BaseTokenException
    else:
        if token_expired(token.exp):
            raise TokenExpiredError

        if token.token_type != TokenTypeEnum.refresh_type:
            logging.warning(
                f"Incorrect token type: {token.token_type}. Should be: {TokenTypeEnum.refresh_type}"
            )
            raise InvalidTokenTypeError

    return token
