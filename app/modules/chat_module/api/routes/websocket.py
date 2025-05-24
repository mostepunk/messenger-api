from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import HTMLResponse

from app.dependencies.services_dependency import get_service
from app.modules.chat_module.resources.html_chat import HTML_CHAT
from app.modules.chat_module.services.websocket_service import WebsocketService

router = APIRouter()


@router.get("/html", summary="WebUI для чата")
async def get():
    return HTMLResponse(HTML_CHAT)


@router.websocket("/{chat_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    service: Annotated[get_service(WebsocketService), Depends()],
):
    await service.handle_incoming_connection(websocket, chat_id)
