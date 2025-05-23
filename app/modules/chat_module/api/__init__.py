from fastapi import APIRouter

from .routes import chats

router = APIRouter(
    tags=["chat"],
    prefix="/chats",
)


router.include_router(chats.router)
