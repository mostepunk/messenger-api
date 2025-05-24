from fastapi import APIRouter

from .routes import chats, websocket

router = APIRouter(
    tags=["Модуль чатов"],
    prefix="/chats",
)


router.include_router(chats.router)
router.include_router(websocket.router)
