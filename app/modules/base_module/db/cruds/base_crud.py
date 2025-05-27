import logging
from typing import Any, Generic, Iterable, Literal, TypeVar, Union
from uuid import UUID

from psycopg.errors import UniqueViolation
from pydantic import TypeAdapter
from sqlalchemy import delete, func, insert, inspect, select, update
from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.base_module.db.errors import (
    BaseDBError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from app.modules.base_module.db.models import Base
from app.modules.base_module.schemas.base import BaseSchema
from app.settings import config

S_in = TypeVar("S_in", bound=BaseSchema)
S_out = TypeVar("S_out", bound=BaseSchema)
T = TypeVar("T", bound=Base)


class BaseCRUD(Generic[S_in, S_out, T]):
    _in_schema: type[S_in]
    _out_schema: type[S_out]
    _table: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, in_schema: S_in, return_raw: bool = False) -> S_out:
        """Добавление записи в соответствующую таблицу

        Args:
            in_schema: Объект схемы создания записи

        Returns:
            object: Объект схемы записи из БД

        """
        values = (
            in_schema.model_dump(exclude_unset=True)
            if isinstance(in_schema, BaseSchema)
            else in_schema
        )
        try:
            query = insert(self._table).values(**values).returning(self._table)
            item = await self.session.scalar(query)
        except IntegrityError as err:
            logging.warning(f"DatabaseError: {err.orig}")
            if isinstance(err.orig, UniqueViolation):
                raise ItemAlreadyExistsError
            else:
                raise BaseDBError from err

        await self.await_relations(item)
        if return_raw:
            return item
        return self._out_schema.model_validate(item)

    async def add_many(self, in_schema: list[Union[S_in, dict]]) -> list[S_out]:
        """Добавление нескольких записей в соответствующую таблицу

        Args:
            in_schema: Список объектов схемы создания

        Returns:
            object: Список объектов схем записей из БД
        """
        if in_schema:
            validator = TypeAdapter(list[self._out_schema])
            q = insert(self._table).values(in_schema).returning(self._table)
            results = await self.session.scalars(q)
            return validator.validate_python(results)

    async def get_all(self) -> list[S_out]:
        """Получение всех записей таблицы

        Returns:
            object: Список объектов схем записей из БД
        """
        validator = TypeAdapter(list[self._out_schema])
        results = await self.session.scalars(select(self._table))
        return validator.validate_python(results)

    async def get_by_id(self, item_uuid: UUID, return_raw: bool = False) -> S_out:
        """Получение записи по уникальному идентификатору

        Args:
            item_uuid: Уникальный идентификатор записи
            return_raw: признак надо ли возвращать модель

        Returns:
            object: Схема объекта записи из БД
        """
        item = await self.session.get(self._table, item_uuid)
        if not item:
            raise ItemNotFoundError(f"Item {item_uuid} not found")
        if return_raw:
            return item
        return self._out_schema.model_validate(item)

    async def get_by_ids(
        self, ids: list[UUID], return_raw: bool = False
    ) -> list[S_out]:
        query = select(self._table).where(self._table.id.in_(ids))
        items = (await self.session.scalars(query)).all()
        if return_raw:
            return items
        validator = TypeAdapter(list[self._out_schema])
        return validator.validate_python(items)

    async def find_catalogues_by_ids(self, catalogue: T, ids: list[UUID]) -> list[T]:
        query = select(catalogue).where(catalogue.id.in_(ids))
        return (await self.session.scalars(query)).all()

    async def update(
        self, item_uuid: UUID, data: Union[dict, S_in], validate: bool = True
    ):
        """Обновление записи в бд по уникальному идентификатору

        Args:
            item_uuid: Уникальный идентификатор записи
            data: Данные для обновления

        Returns:
            object: Схема объекта записи из БД
        """
        if isinstance(data, BaseSchema):
            data = data.model_dump()
        q = (
            update(self._table)
            .where(self._table.id == item_uuid)
            .values(data)
            .returning(self._table)
        )
        result = await self.session.scalar(q)
        await self.await_relations(result)
        if result:
            if validate:
                return self._out_schema.model_validate(result)
            return result
        raise ItemNotFoundError(f"Item {item_uuid} not found")

    async def update_many(self, values: list[dict[str, Any]], table: T = None):
        for chunk in self.split_into_chunks(values):
            await self.session.execute(update(self._table), chunk)
            logging.debug(f"Update {len(chunk)} chunks")

    async def delete(self, item_uuid: UUID):
        """Удаление записи из БД по уникальному идентификатору

        Args:
            item_uuid: Уникальный идентификатор записи

        Returns:
            None
        """
        q = (
            delete(self._table)
            .where(self._table.id == item_uuid)
            .returning(self._table)
        )
        item = await self.session.scalar(q)
        if item is None:
            raise ItemNotFoundError(f"Item {item_uuid} not found")

    async def delete_many(self, ids: list[UUID], table: T = None):
        """Удаление записи из БД по уникальным идентификаторам

        Args:
            ids: список ID

        Returns:
            None
        """
        table_to_delete = table or self._table
        q = delete(table_to_delete).where(table_to_delete.id.in_(ids))
        await self.session.execute(q)

    def _filters(
        self, columns: dict[str, Any], filter_type: Literal["ilike", "equals"]
    ):
        query_filters = []
        for key, value in columns.items():
            if not value or not hasattr(self._table, value):
                continue

            if filter_type == "ilike":
                query_filters.append(getattr(self._table, key).ilike(f"%{value}%"))

            elif filter_type == "equals":
                query_filters.append(getattr(self._table, key) == value)

        return query_filters

    async def paginated_select(
        self,
        query: select,
        limit: int,
        offset: int,
    ) -> tuple[int, ScalarResult]:
        """Помимо выполнения запроса к БД вертает общее кол-во.

        и передает параметры пагинации, если это необходимо.

        Args:
            query(select): select query
            limit (int): limit
            offset (int): offset

        Returns:
            Tuple[int, ChunkedIteratorResult]:
        """
        total_query = select(func.count()).select_from(query.subquery())
        total_count = await self.session.scalar(total_query)

        if all((limit is not None, offset is not None)):
            query = query.limit(limit).offset(offset * limit)

        return total_count, await self.session.scalars(query)

    def get_relationship_names(self):
        """После обновления таблицы, может возникнуть ошибка GreenletSpawn.
        Довольно неприятная вещь, связанная с тем, что невозможно обратиться к
        relationship если он не был загружен в options

        https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncAttrs.awaitable_attrs
        """
        mapper = inspect(self._table)

        return [rel.key for rel in mapper.relationships]

    async def await_relations(self, item: T):
        relationships = self.get_relationship_names()
        if not relationships:
            return
        for relation in relationships:
            await getattr(item.awaitable_attrs, relation)

    def split_into_chunks(
        self,
        seq: Iterable,
        size: int = config.db.chunk_size,
    ) -> Iterable:
        """Разбивает список на части.

        Используется для вставки данных по частям, если данных придет слишком много.
        """
        for pos in range(0, len(seq), size):
            yield seq[pos : pos + size]
