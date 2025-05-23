from pydantic import Field, field_validator

from app.modules.base_module.schemas.base import BaseSchema


class PaginationParams(BaseSchema):
    limit: int | None = Field(
        default=None,
        ge=1,
        examples=10,
        description="Maximum number of results on the page",
    )
    offset: int | None = Field(
        default=None,
        ge=0,
        examples=1,
        description="Requested page number",
    )

    @field_validator("offset", mode="before")
    def validate_offset(cls, offset):
        """Уменьшить offset на 1 для правильной работы select

        Фронт нумерует страницы начиная с единицы.
        """
        if offset is not None:
            return offset - 1 if offset != 0 else 0


class Paginator(PaginationParams):
    total_count: int = Field(
        ge=0,
        examples=10,
        description="Total count of query results",
        alias="totalCount",
    )
