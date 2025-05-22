import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.modules.base_module.errors import AppValidationException


def to_camel(snake_str: str) -> str:
    """автоматическое создание camelCase alias.

    _hello_world -> helloWorld
    """
    snake_str = snake_str.strip("_")
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
        # strip_whitespace=True,
        use_enum_values=True,
        from_attributes=True,
    )

    def json(self, exclude_unset: bool = False):
        return self.model_dump(mode="json", by_alias=True, exclude_unset=exclude_unset)

    def dict(self, exclude_unset: bool = False):
        return self.model_dump(exclude_unset=exclude_unset)

    @field_validator("*", mode="before")
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class CustomBaseSchema(BaseSchema):
    pass


class BaseDB(BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


# TODO: Почистить bCUD схемы
# DELETE
class DeleteItem(BaseSchema):
    id: UUID


# DELETE
class ABCBulkSchema(CustomBaseSchema):
    """Проверка на дубликаты ID в массивах среди bCUD объектов"""

    @model_validator(mode="after")
    def check_duplicate_ids(self) -> "ABCBulkSchema":
        id_map: dict[UUID, set[str]] = {}
        errors: list[dict[str, str]] = []

        def extract_id(item: Any) -> UUID | None:
            if isinstance(item, UUID):
                return item
            elif isinstance(item, dict):
                return item.get("id")
            elif hasattr(item, "id"):
                return getattr(item, "id")
            return None

        def collect_ids(field_name: str):
            items = getattr(self, field_name, None)
            for item in items or []:
                _id = extract_id(item)
                if _id:
                    id_map.setdefault(_id, set()).add(field_name)

        # Собираем все ID из доступных полей
        for field in ("create", "update", "delete"):
            if hasattr(self, field):
                collect_ids(field)

        # Конфликты между массивами
        for _id, sources in id_map.items():
            if len(sources) > 1:
                for source in sources:
                    errors.append(
                        {
                            "field": [self.__class__.__name__, f"${source}"],
                            "code": "BULK_CUD_ERROR",
                            "text": f"ID dublicates in {', '.join(sources)}",
                            "input": str(_id),
                        }
                    )

        # Дубли внутри одного массива
        for field in ("create", "update", "delete"):
            if not hasattr(self, field):
                continue
            items = getattr(self, field)
            ids = [extract_id(item) for item in items or [] if extract_id(item)]
            seen = set()
            duplicates = {id_ for id_ in ids if id_ in seen or seen.add(id_)}
            if duplicates:
                errors.append(
                    {
                        "field": [self.__class__.__name__, field],
                        "code": "BULK_CUD_ERROR",
                        "text": f"Дублирующиеся ID в '{field}': {', '.join(str(d) for d in duplicates)}",
                        "input": ", ".join(str(d) for d in duplicates),
                    }
                )

        if errors:
            logging.warning(f"ABC errors: {errors}")
            err = AppValidationException()
            err.fields = errors
            raise err

        return self


# DELETE
class BaseBulkCUDSchema(ABCBulkSchema):
    delete: list[DeleteItem] | None = Field(None, alias="$delete")
    create: list[Any] | None = Field(None, alias="$create")
    update: list[Any] | None = Field(None, alias="$update")


@dataclass
class SelectEnum:
    """Класс для enums"""

    key: str
    value: str


class StrEnum(str, Enum):
    """Parent Custom Enum Str"""

    phrase: str

    def __new__(cls, value: str, phrase: str = None):
        obj = str.__new__(cls, value)

        obj._value_ = value
        obj.phrase = phrase

        return obj

    def __str__(self) -> str:
        return self._value_

    @classmethod
    @property
    def choices(cls) -> list[SelectEnum]:
        return [
            SelectEnum(
                key=attr.value,
                value=attr.phrase,
            )
            for attr in list(cls)
        ]


class BaseTotalSchema(BaseSchema):
    total_count: int | None = None
    entities: list[dict]
