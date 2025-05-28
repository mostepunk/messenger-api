from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.modules.chat_module.resources.html_chat import HTML_CHAT

router = APIRouter()


@router.get("/ui/", summary="WebUI для чата")
async def get():
    return HTMLResponse(HTML_CHAT)
