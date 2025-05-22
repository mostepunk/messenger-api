import logging

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.fastapi_engine.events.error_event import init_error_handler
from app.fastapi_engine.events.startup import startup_application
from app.fastapi_engine.middlewares import add_corse_middleware
from app.fastapi_engine.middlewares.success_middleware import add_meta_middleware
from app.settings import config

logging.basicConfig(
    filename=config.log.access_log_path if config.log.write_to_file else None,
    encoding="utf-8",
    level=config.log.logging_level,
    format=config.log.format,
)


def get_fastapi_app() -> FastAPI:
    app = FastAPI(
        **config.app.api_settings,
        lifespan=startup_application,
    )

    add_corse_middleware(app)
    add_meta_middleware(app)
    init_error_handler(app)

    # if config.log.enable:
    #     add_logging_middleware(app)

    @app.get("/", include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url=config.app.prefix + config.app.doc_path)

    return app
