from fastapi import HTTPException, status

from app.utils.errors_map import ErrorCode


class BaseAppException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Unknown Error"
    code = ErrorCode.unknown

    def __init__(self, detail: str = "") -> None:
        super().__init__(self.status_code, detail=detail or self.detail)
