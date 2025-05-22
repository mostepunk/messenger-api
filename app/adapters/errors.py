from fastapi import status

from app.modules.base_module.errors import BaseAppException
from app.utils.errors_map import ErrorCode


class ClientError(BaseAppException):
    detail = "External connection error"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = ErrorCode.external_client_error
