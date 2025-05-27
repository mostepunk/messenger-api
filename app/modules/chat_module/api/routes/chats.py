from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies.services_dependency import get_service
from app.modules.auth_module.dependencies.jwt_decode import get_account_from_token
from app.modules.base_module.schemas.pagination import PaginationParams
from app.modules.chat_module.schemas.chat_schemas import (
    ChatSchema,
    CreateChatSchema,
    DetailedChatSchema,
    UpdateChatSchema,
)
from app.modules.chat_module.schemas.message_schema import MessageEntities
from app.modules.chat_module.services.chat_service import ChatService

router = APIRouter()


@router.get("/", response_model=list[ChatSchema], summary="Список чатов")
async def get_chats(
    service: Annotated[get_service(ChatService), Depends()],
    account: Annotated[get_account_from_token, Depends()],
):
    return await service.accounts_chats(account.id)


@router.post("/", response_model=ChatSchema, summary="Создать чат")
async def create_chat(
    service: Annotated[get_service(ChatService), Depends()],
    account: Annotated[get_account_from_token, Depends()],
    data: CreateChatSchema,
):
    return await service.create_chat(account.id, data)


@router.get("/{chat_id}/", response_model=DetailedChatSchema, summary="Детали чата")
async def chat_info(
    service: Annotated[get_service(ChatService), Depends()],
    account: Annotated[get_account_from_token, Depends()],
    chat_id: UUID,
):
    return await service.chat_info(account.id, chat_id)


@router.put("/{chat_id}/", response_model=ChatSchema, summary="Обновить чат")
async def update_chat(
    service: Annotated[get_service(ChatService), Depends()],
    account: Annotated[get_account_from_token, Depends()],
    chat_id: UUID,
    data: UpdateChatSchema,
):
    return await service.update_chat(account.id, data, chat_id)


@router.delete("/{chat_id}/", summary="Удалить чат")
async def delete_chat(
    service: Annotated[get_service(ChatService), Depends()],
    account: Annotated[get_account_from_token, Depends()],
    chat_id: UUID,
):
    return await service.delete_chat(account.id, chat_id)


@router.get(
    "/{chat_id}/history/", response_model=MessageEntities, summary="История чата"
)
async def chat_history(
    service: Annotated[get_service(ChatService), Depends()],
    account: Annotated[get_account_from_token, Depends()],
    chat_id: UUID,
    pagination: Annotated[PaginationParams, Depends()],
):
    return await service.chat_history(account.id, chat_id, pagination)
