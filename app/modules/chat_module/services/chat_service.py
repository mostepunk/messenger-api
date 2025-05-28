import logging
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

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
    from app.modules.chat_module.schemas.profile_schemas import ProfileDBSchema


class ChatService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.chat_crud = ChatCRUD(session)
        self.profile_crud = ProfileCRUD(session)
        self.message_crud = MessageCRUD(session)

    async def accounts_chats(self, account_id: UUID):
        profile_db: "ProfileDBSchema" = (
            await self.profile_crud.get_profile_by_account_id(account_id)
        )
        logging.info(f"Profile.ID {profile_db.id} has {len(profile_db.chats)} chats")
        return profile_db.chats

    async def create_chat(self, account_id: UUID, chat_data: CreateChatSchema):
        values = chat_data.model_dump(exclude_unset=True)
        profile_db: "ProfileDBSchema" = (
            await self.profile_crud.get_profile_by_account_id(account_id)
        )

        members = values.pop("members", [])
        if profile_db.id not in members:
            members.append(profile_db.id)

        values["owner_id"] = profile_db.id

        chat = await self.chat_crud.add(values)
        profiles: list["ProfileModel"] = await self.profile_crud.get_by_ids(
            members, return_raw=True
        )

        if len(profiles) != len(members):
            not_found = list(set(members) - set([p.id for p in profiles]))
            raise MembersNotFound(f"{len(not_found)} members not found: {not_found}")

        await self.chat_crud.add_members(chat.id, members)
        await self.session.commit()
        logging.info(f"Chat.ID {chat.id} with {len(members)} members created")
        return chat

    async def delete_chat(self, account_id: UUID, chat_id: UUID):
        profile_db: "ProfileDBSchema" = (
            await self.profile_crud.get_profile_by_account_id(account_id)
        )
        if not profile_db.is_owner_of_chat(chat_id):
            raise ProhibitedToModifyChat()

        await self.chat_crud.delete(chat_id)
        await self.session.commit()
        logging.debug(f"Chat.ID {chat_id} deleted")

    async def update_chat(
        self, account_id: UUID, chat_data: CreateChatSchema, chat_id: UUID
    ):
        profile_db: "ProfileDBSchema" = (
            await self.profile_crud.get_profile_by_account_id(account_id)
        )

        if not profile_db.is_owner_of_chat(chat_id):
            raise ProhibitedToModifyChat()

        values = chat_data.model_dump(exclude_unset=True)
        members = values.pop("members", [])
        members.append(profile_db.id)

        chat = await self.chat_crud.update(chat_id, values)
        profiles: list["ProfileModel"] = await self.profile_crud.get_by_ids(
            members, return_raw=True
        )

        if len(profiles) != len(members):
            not_found = list(set(members) - set([p.id for p in profiles]))
            raise MembersNotFound(f"{len(not_found)} members not found: {not_found}")

        chat_members = [member.id for member in chat.members]
        new_members = list(set(members) - set(chat_members))
        if new_members:
            await self.chat_crud.add_members(chat.id, new_members)

        await self.session.commit()
        logging.debug(f"Chat.ID {chat.id} with {len(members)} members updated")
        return chat

    async def chat_info(self, account_id: UUID, chat_id: UUID):
        profile_db: "ProfileDBSchema" = (
            await self.profile_crud.get_profile_by_account_id(account_id)
        )
        if not profile_db.is_memeber_of_chat(chat_id):
            raise AccessDenied("Only chat members can see chat info")

        chat = await self.chat_crud.full_chat_info(chat_id)
        logging.debug(f"Found {chat}")
        return chat

    async def chat_history(self, account_id: UUID, chat_id: UUID, pagination: dict):
        profile_db: "ProfileDBSchema" = (
            await self.profile_crud.get_profile_by_account_id(account_id)
        )

        chat = profile_db.find_chat(chat_id)
        if chat is None:
            raise ChatNotFound()

        if chat_id not in profile_db.chat_ids:
            raise AccessDenied()

        total, messages = await self.message_crud.chat_history(
            chat_id, **pagination.model_dump(exclude_unset=True)
        )

        logging.info(
            f"Chat.ID {chat.id} total {total} messages. Return {len(messages)} messages"
        )
        return {"total_count": total, "entities": messages}
