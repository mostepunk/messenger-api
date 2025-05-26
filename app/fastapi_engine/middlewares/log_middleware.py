import logging

from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask

from app.settings import config


def log_info(req_body: bytes, res_body: bytes, *args, **kwargs):
    log_item = {"Request": {}, "Response": {}}

    log_item["Request"]["headers"] = kwargs["kwargs"].get("req_headers")
    req_headers = kwargs["kwargs"].get("req_headers", {})
    safe_headers = {
        k: v
        for k, v in req_headers.items()
        if k.lower() not in ["authorization", "cookie", "x-api-key"]
    }
    log_item["Request"]["headers"] = safe_headers
    log_item["Response"]["status_code"] = kwargs["kwargs"].get("status_code")

    try:
        log_item["Request"]["body"] = req_body.decode("utf-8")
    except UnicodeDecodeError:
        log_item["Request"]["body"] = req_body

    try:
        log_item["Response"]["body"] = res_body.decode("utf-8")
    except UnicodeDecodeError:
        log_item["Response"]["body"] = res_body

    logging.info(log_item)


async def log_middleware(request: Request, call_next):
    task = None
    req_body = await request.body()
    response = await call_next(request)

    res_body = b""
    async for chunk in response.body_iterator:
        res_body += chunk

    if request.url.path not in config.app.no_log:
        task = BackgroundTask(
            log_info,
            req_body,
            res_body,
            kwargs={
                "req_headers": dict(request.headers),
                "resp_headers": dict(response.headers),
                "status_code": response.status_code,
            },
        )

    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=task,
    )


def add_logging_middleware(app: FastAPI):
    logging.warning("LoggingMiddleware Enabled")
    app.middleware("http")(log_middleware)
