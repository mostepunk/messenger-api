import logging
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth_module.db.cruds.account_crud import AccountCRUD
from app.modules.base_module.services.base_service import BaseService
from app.modules.chat_module.db.cruds.chat_crud import ChatCRUD
from app.modules.chat_module.db.cruds.message_crud import MessageCRUD
from app.modules.chat_module.db.cruds.profile_crud import ProfileCRUD
from app.modules.chat_module.errors import (
    AccessDenied,
    ChatNotFound,
    MembersNotFound,
    ProhibitedToModifyChat,
)
from app.modules.chat_module.schemas.chat_schemas import CreateChatSchema

if TYPE_CHECKING:
    from app.modules.auth_module.schemas.account import AccountDBSchema
    from app.modules.chat_module.db.models.profile import ProfileModel


class ChatService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.chat_crud = ChatCRUD(session)
        self.account_crud = AccountCRUD(session)
        self.profile_crud = ProfileCRUD(session)
        self.message_crud = MessageCRUD(session)

    async def accounts_chats(self, account_id: UUID):
        account_db: "AccountDBSchema" = await self.account_crud.get_by_id(account_id)
        logging.info(
            f"Account.ID {account_db.id} has {len(account_db.profile.chats)} chats"
        )
        return account_db.profile.chats

    async def create_chat(self, account_id: UUID, chat_data: CreateChatSchema):
        values = chat_data.model_dump(exclude_unset=True)
        account_db: "AccountDBSchema" = await self.account_crud.get_by_id(account_id)

        members = values.pop("members", [])
        if account_db.profile.id not in members:
            members.append(account_db.profile.id)

        values["owner_id"] = account_db.profile.id

        chat = await self.chat_crud.add(values)
        profiles: list["ProfileModel"] = await self.profile_crud.get_by_ids(
            members, return_raw=True
        )

        if len(profiles) != len(members):
            not_found = list(set(members) - set([p.id for p in profiles]))
            raise MembersNotFound(f"{len(not_found)} members not found: {not_found}")

        await self.chat_crud.add_members(chat.id, profiles)
        await self.session.commit()
        logging.info(f"Chat.ID {chat.id} with {len(members)} members created")
        return chat

    async def delete_chat(self, account_id: UUID, chat_id: UUID):
        account_db: "AccountDBSchema" = await self.account_crud.get_by_id(account_id)

        if not self.is_account_owner(account_db, chat_id):
            raise ProhibitedToModifyChat()

        await self.chat_crud.delete(chat_id)
        await self.session.commit()
        logging.info(f"Chat.ID {chat_id} deleted")

    async def update_chat(
        self, account_id: UUID, chat_data: CreateChatSchema, chat_id: UUID
    ):
        account_db: "AccountDBSchema" = await self.account_crud.get_by_id(account_id)

        if not self.is_account_owner(account_db, chat_id):
            raise ProhibitedToModifyChat()

        values = chat_data.model_dump(exclude_unset=True)
        members = values.pop("members", [])
        members.append(account_db.profile.id)

        chat = await self.chat_crud.update(chat_id, values)
        profiles: list["ProfileModel"] = await self.profile_crud.get_by_ids(
            members, return_raw=True
        )

        if len(profiles) != len(members):
            not_found = list(set(members) - set([p.id for p in profiles]))
            raise MembersNotFound(f"{len(not_found)} members not found: {not_found}")

        await self.chat_crud.add_members(chat.id, profiles)
        await self.session.commit()
        logging.info(f"Chat.ID {chat.id} with {len(members)} members updated")
        return chat

    async def chat_info(self, account_id: UUID, chat_id: UUID):
        account_db: "AccountDBSchema" = await self.account_crud.get_by_id(account_id)

        chat = await self.chat_crud.full_chat_info(chat_id)
        logging.info(f"Found {chat}")
        return chat

    async def chat_history(self, account_id: UUID, chat_id: UUID, pagination: dict):
        account_db: "AccountDBSchema" = await self.account_crud.get_by_id(account_id)

        chat = account_db.profile.find_chat(chat_id)
        if chat is None:
            raise ChatNotFound()

        if chat_id not in account_db.profile.chat_ids():
            raise AccessDenied()

        total, messages = await self.message_crud.chat_history(
            chat_id, **pagination.model_dump(exclude_unset=True)
        )

        logging.info(
            f"Chat.ID {chat.id} total {total} messages. Return {len(messages)} messages"
        )
        return {"total_count": total, "entities": messages}

    def is_account_owner(self, account_db: "AccountDBSchema", chat_id: UUID) -> bool:
        profile_id = account_db.profile.id
        profile_owned_chats = [
            chat.id for chat in account_db.profile.chats if chat.owner.id == profile_id
        ]

        if chat_id in profile_owned_chats:
            return True
        return False
