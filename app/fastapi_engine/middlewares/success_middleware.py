import json

from fastapi import FastAPI, Request, Response

IGNORE_PATH = {
    "/openapi.json",
    "/docs",
    "/accounts/sign-in/swagger/",
}


async def add_meta_to_answer(request: Request, call_next) -> Response:
    """Добавить метаинформацию об успешных ответах.

    new_body = {"status": "success", "data": body_response}

    Args:
        request (Request): request
        call_next:
    """
    if request.url.path in IGNORE_PATH:
        return await call_next(request)

    response = await call_next(request)

    if response.status_code == 200:
        res_body = b""
        async for chunk in response.body_iterator:
            res_body += chunk

        try:
            body_response = res_body.decode("utf-8")
            body_response = json.loads(body_response)
        except (UnicodeDecodeError, json.JSONDecodeError):
            res = Response(
                content=res_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
            res.headers["Content-Length"] = str(len(res_body))
            return res

        new_body = {"status": "success", "data": body_response}
        new_body = json.dumps(new_body)

        res = Response(
            content=new_body.encode(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type="application/json",
        )

        res.headers["Content-Length"] = str(len(new_body))
        return res

    return response


def add_meta_middleware(app: FastAPI):
    app.middleware("http")(add_meta_to_answer)
