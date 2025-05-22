from fastapi import status

from app.modules.base_module.errors import BaseAppException
from app.utils.errors_map import ErrorCode


class BaseNotificationException(BaseAppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = ErrorCode.notify_error
    detail = "Notification Exception"


class NotificationTypeNotAllowed(BaseNotificationException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    detail = "Notification type not allowed"
