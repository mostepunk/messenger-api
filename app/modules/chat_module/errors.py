from fastapi import status

from app.modules.base_module.errors import BaseAppException
from app.utils.errors_map import ErrorCode


class BaseChatException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Chat error"
    code = ErrorCode.chat_error


class MembersNotFound(BaseChatException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Members not found"
    code = ErrorCode.member_not_found


class ProhibitedToModifyChat(BaseChatException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Prohibited to delete chat"
    code = ErrorCode.prohibited_to_delete


class ChatNotFound(BaseChatException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Chat not found"
    code = ErrorCode.not_found


class AccessDenied(BaseChatException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access denied"
    code = ErrorCode.auth_error
