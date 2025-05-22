from datetime import datetime, timedelta
from uuid import UUID

import jwt

from app.modules.auth_module.schemas.token import Token, TokenTypeEnum
from app.settings import config


def create_confirmation_token(account_id: UUID, account_email: str) -> str:
    return create_token(
        Token(
            token_type=TokenTypeEnum.confirmation_type,
            user_id=account_id,
            email=account_email,
            exp=datetime.now()
            + timedelta(days=config.jwt.confirmation_token_expire_days),
        )
    )


def create_access_token(account_id: UUID, account_email: str) -> str:
    return create_token(
        Token(
            token_type=TokenTypeEnum.access_type,
            user_id=account_id,
            email=account_email,
            exp=datetime.now()
            + timedelta(minutes=config.jwt.access_token_expire_minutes),
        )
    )


def create_refresh_token(account_id: UUID, account_email: str) -> str:
    return create_token(
        Token(
            token_type=TokenTypeEnum.refresh_type,
            user_id=account_id,
            email=account_email,
            exp=datetime.now() + timedelta(days=config.jwt.refresh_token_expire_days),
        )
    )


def create_token(token: Token) -> str:
    encoded_jwt: str = jwt.encode(
        token.json(), config.jwt.secret_key, algorithm=config.jwt.alg
    )
    return encoded_jwt
