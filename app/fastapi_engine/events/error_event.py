import code
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.responses import JSONResponse

from app.modules.base_module.errors import BaseAppException
from app.utils.err_message import err_msg
from app.utils.errors_map import ErrorCode


def init_error_handler(app: FastAPI):

    @app.exception_handler(BaseAppException)
    async def app_error_handler(_: Request, err: BaseAppException) -> JSONResponse:
        return err_msg(
            status_code=err.status_code,
            error_body={
                "status": "error",
                "error": {"code": err.code, "message": err.detail},
            },
        )

    @app.exception_handler(HTTPException)
    async def base_error_handler(_: Request, err: HTTPException) -> JSONResponse:
        return err_msg(
            status_code=err.status_code,
            error_body={
                "status": "error",
                "error": {"code": code, "message": err.detail},
            },
        )

    @app.exception_handler(Exception)
    async def exception_error_handler(_: Request, err: Exception) -> JSONResponse:
        logging.warning(f"SystemError: {err}")
        return err_msg(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_body={
                "status": "error",
                "error": {"code": ErrorCode.system_error, "message": str(err)},
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        fields = []
        for error in exc.errors():
            fields.append(
                {
                    "field": error.get("loc"),
                    "code": error.get("type"),
                    "text": error.get("msg"),
                    "input": error.get("input"),
                }
            )
        return err_msg(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_body={
                "status": "error",
                "error": {
                    "code": ErrorCode.unexpected_validation_error,
                    "message": f"{len(fields)} errors in schema",
                    "fields": fields,
                },
            },
        )
