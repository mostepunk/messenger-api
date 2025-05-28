from fastapi import APIRouter

from .routes import chats, ui, websocket

router = APIRouter(
    tags=["Модуль чатов"],
    prefix="/chats",
)


router.include_router(ui.router)
router.include_router(chats.router)
router.include_router(websocket.router)
