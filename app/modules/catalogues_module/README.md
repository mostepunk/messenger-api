# Модуль справочников
Справочные данные для проекта

## Описание модуля
```
 catalogues_module
 ├── api
 │   └── routes
 │       └── principal_statuses.py
 ├── db
 │   ├── cruds
 │   │   └── model_crud.py
 │   └── models
 │       └── model.py
 ├── dependencies
 ├── readme.md
 ├── schemas
 │   ├── catalogues.py
 │   └── enums.py
 ├── services
 │   └── catalogue_service.py
 └── tests
```
## Правила работы с каталогами:
- Имя модели должно строго следовать правилам:
    - Имя должно начинаться с `catalogue_`
    - После этого префикса должно идти имя с нижним подчерком `table_name`
    - Итого полное имя справочника: `catalogue_table_name`
- Имя ендпоинта должно подчиняться правилам:
    - Для каждой модели генерируется ендпоинт в `/catalogues/`
    - Имя ендпоинта совпадает с названием таблицы, только вместо нижнего подчерка - дефис:
        - `catalogue_table_name` -> `/catalogues/table-name/`

Такие строгие правила нужны, потому что в проекте используется большое кол-во справочной инфы. 
На фронт надо отдавать генерируемый роут. Пример используется в `app.modules.catalogues_module.schemas.catalogues.APICatalogueSchema`
```python
class APICatalogueSchema(BaseCatalogueSchema):
    id: UUID
    route: str | None = None

    @model_validator(mode="before")
    def get_route_from_sql_tablename(self) -> Self:
        """Изменить имя каталога на путь к АПИ каталогу:

        catalogue_table_name -> /catalogues/table-name/
        """
        tablename = self.__tablename__
        route_path = tablename.replace("catalogue_", "catalogues/").replace("_", "-")
        self.route = f"/{route_path}/"
        return self
```
