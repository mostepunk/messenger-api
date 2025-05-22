import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def startup_application(app: FastAPI):
    """
    Переопределение вызовов при старте приложения.

    Вся функциональность до yield выполняется при старте приложения.
    Вся функциональность после yield выполняется при остановке приложения.

    """
    logging.info("Startup application")
    yield
    logging.info("Shutdown application")
