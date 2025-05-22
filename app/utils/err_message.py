from fastapi.responses import JSONResponse


def err_msg(status_code: int, error_body: dict) -> JSONResponse:
    """Схема возврата ошибки"""
    return JSONResponse(content=error_body, status_code=status_code)
