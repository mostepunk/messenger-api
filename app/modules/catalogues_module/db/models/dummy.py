from app.modules.catalogues_module.db.models.base_catalogue import BaseCatalogueModel


class DummyModel(BaseCatalogueModel):
    __tablename__ = "catalogue_test"
