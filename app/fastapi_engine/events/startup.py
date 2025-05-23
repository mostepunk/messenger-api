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
    from app.modules.chat_module.schemas.profile_schemas import ProfileDBSchema, ProfileSchema
    from app.modules.auth_module.schemas.account import AccountDBSchema
    from app.modules.chat_module.schemas.chat_schemas import ChatSchema, ChatDBSchema, DetailedChatSchema

    AccountDBSchema.model_rebuild()
    ChatSchema.model_rebuild()
    ProfileDBSchema.model_rebuild()
    DetailedChatSchema.model_rebuild()

    yield
    logging.info("Shutdown application")
