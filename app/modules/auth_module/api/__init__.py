from fastapi import APIRouter

from .routes import auth

router = APIRouter(
    tags=["Модуль авторизации"],
    prefix="/accounts",
)

router.include_router(auth.router)
