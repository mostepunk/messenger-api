from typing import Self
from uuid import UUID

from pydantic import Field, model_validator

from app.modules.base_module.schemas.base import BaseSchema


class BaseCatalogueSchema(BaseSchema):
    key: str
    value: str


class APICatalogueSchema(BaseCatalogueSchema):
    id: UUID
    route: str | None = None

    @model_validator(mode="before")
    def get_route_from_sql_tablename(self) -> Self:
        """Изменить имя каталога на путь к АПИ каталогу:

        catalogue_table_name -> /catalogues/table-name/
        """
        if not hasattr(self, "__tablename__"):
            return self
        tablename = self.__tablename__
        route_path = tablename.replace("catalogue_", "catalogues/").replace("_", "-")
        self.route = f"/{route_path}/"
        return self


class CatalogueSchema(BaseCatalogueSchema):
    key: str = Field(example="preInvestigationCheck")
    value: str = Field(example="Доследственная проверка")
