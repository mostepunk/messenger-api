from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.settings import config


def add_corse_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.app.allowed_hosts,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Authorization",
        ],
    )
