from fastapi import status

from app.modules.base_module.errors import BaseAppException
from app.utils.errors_map import ErrorCode


class BaseDBError(BaseAppException):
    detail = "DataBase error"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = ErrorCode.database_error


class ItemNotFoundError(BaseDBError):
    status_code = status.HTTP_404_NOT_FOUND
    code = ErrorCode.not_found
    detail = "Item not found"


class ItemAlreadyExistsError(BaseDBError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Item already exists"
