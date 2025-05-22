from fastapi import status

from app.modules.base_module.errors import AppValidationException, BaseAppException
from app.utils.errors_map import ErrorCode


class AuthException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not allowed"
    code = ErrorCode.auth_error


class CredentialsError(AuthException):
    detail = "Credentials invalid"


class AccountAlreadyVerified(AuthException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Account already confirmed"


class AccountAlreadyExists(AuthException):
    status_code = status.HTTP_409_CONFLICT
    code = ErrorCode.account_already_exists
    detail = "Account already exists"


class AccountNotExists(AuthException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = ErrorCode.account_not_found
    detail = "Account not found"


class AuthValidationException(AppValidationException):
    pass


class AuthIncorrectEmailError(AuthValidationException):
    detail = "Email invalid"


class AuthIncorrectPasswordError(AuthValidationException):
    detail = "Password invalid"
