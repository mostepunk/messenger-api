from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.chat_module.db.models.profile import ProfileModel
from app.modules.chat_module.schemas.profile_schemas import (
    ProfileDBSchema,
    ProfileSchema,
)


class ProfileCRUD(BaseCRUD[ProfileSchema, ProfileDBSchema, ProfileModel]):
    _in_schema = ProfileSchema
    _out_schema = ProfileDBSchema
    _table = ProfileModel

    def __init__(self, session: AsyncSession):
        self.session = session
