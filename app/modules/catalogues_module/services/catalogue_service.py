from app.modules.base_module.services.base_service import BaseService
from app.modules.catalogues_module.db.catalogue_registry import catalogue_registry
from app.modules.catalogues_module.db.cruds.catalogue_crud import GeneralCatalogueCRUD


class CatalogueService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self.catalogue = GeneralCatalogueCRUD(self.session)

    async def get_catalogue_by_name(self, name: str):
        model_class = catalogue_registry.get(name)
        if not model_class:
            raise ValueError(f"Catalogue '{name}' not found")
        return await self.catalogue.get_catalogue_by_model(model_class)
