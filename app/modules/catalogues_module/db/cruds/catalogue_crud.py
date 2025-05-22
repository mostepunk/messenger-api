from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.base_module.db.cruds.base_crud import BaseCRUD
from app.modules.base_module.db.models.base import Base
from app.modules.catalogues_module.schemas.catalogues import (
    APICatalogueSchema,
    BaseCatalogueSchema,
)


class GeneralCatalogueCRUD(BaseCRUD[BaseCatalogueSchema, APICatalogueSchema, Base]):
    _in_schema = BaseCatalogueSchema
    _out_schema = APICatalogueSchema
    _table = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_catalogue_by_model(self, model_class: type[Base]):
        self._table = model_class
        res = await self.get_all()
        self._table = None
        return res
