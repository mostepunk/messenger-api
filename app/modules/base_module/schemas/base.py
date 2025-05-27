from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


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
