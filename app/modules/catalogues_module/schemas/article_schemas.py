from uuid import UUID

from pydantic import Field

from app.modules.base_module.schemas.base import (
    BaseDB,
    BaseSchema,
)


class ArticleBaseSchema(BaseSchema):
    number: str | None = Field(None, description="номер статьи")
    part: str | None = Field(None, description="часть")
    clause: str | None = Field(None, description="пункт")
    text: str = Field(description="Описание")


class ArticleIDBaseSchema(ArticleBaseSchema):
    id: UUID


class ArticleDBSchema(ArticleBaseSchema, BaseDB):
    pass


class ArticlesFilterSchema(BaseSchema):
    number: str | None = Field(None, description="номер статьи")
    text: str | None = Field(None, description="Описание")


class ArticlesListSchema(BaseSchema):
    total_count: int = Field(alias="totalCount")
    articles: list[ArticleIDBaseSchema]
