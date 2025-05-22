from fastapi import status

from app.modules.base_module.errors import BaseAppException
from app.utils.errors_map import ErrorCode


class BaseTokenException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token Invalid"
    code = ErrorCode.auth_error


class InvalidTokenError(BaseTokenException):
    pass


class InvalidTokenTypeError(InvalidTokenError):
    detail = "Invalid token type"


class TokenDecodeError(BaseTokenException):
    pass


class TokenExpiredError(BaseTokenException):
    detail = "Token expired"
