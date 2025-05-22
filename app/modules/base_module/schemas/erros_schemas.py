from typing import Any, Literal

from pydantic import BaseModel, Field

from app.utils.errors_map import ErrorCode


class ErrorMessageSchema(BaseModel):
    code: ErrorCode = Field(..., title="Код ошибки")
    message: str = Field(..., title="Текст ошибки")


class BaseResponseSchema(BaseModel):
    status: Literal["error", "ok"] = Field(title="Статус")


class ErrorResponseSchema(BaseResponseSchema):
    error: ErrorMessageSchema | None = Field(None, title="Ответ в случае ошибки")


class SuccessResponseSchema(BaseResponseSchema):
    data: Any | None = Field(None, title="Данные ответа")
