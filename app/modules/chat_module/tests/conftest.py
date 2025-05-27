from app.modules.chat_module.schemas.message_schema import MessageSchema, MessageDBSchema
from app.modules.chat_module.schemas.chat_schemas import ChatSchema, ChatDBSchema, DetailedChatSchema
from app.modules.chat_module.schemas.profile_schemas import ProfileDBSchema, ProfileSchema

ChatSchema.model_rebuild()
DetailedChatSchema.model_rebuild()
MessageSchema.model_rebuild()
MessageDBSchema.model_rebuild()
ChatDBSchema.model_rebuild()
ProfileDBSchema.model_rebuild()

