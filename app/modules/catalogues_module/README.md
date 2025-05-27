# Catalogues Module
Модуль справочников для хранения и управления статическими данными приложения, такими как списки стран, статусы, категории и другие справочные значения.

## Назначение модуля

Catalogues Module решает задачи управления справочными данными:

- **Централизованное хранение** справочников
- **Автоматическое создание API** для каждого справочника
- **Унифицированная структура** всех справочников
- **Простое добавление** новых справочников
- **Версионирование данных** через миграции
- **Локализация значений** справочников

## Структура модуля

```
catalogues_module/
├── api/
│   └── routes/
│       └── catalogue_router.py   # Динамически генерируемые эндпоинты
├── db/
│   ├── cruds/
│   │   └── catalogue_crud.py     # Универсальный CRUD для справочников
│   ├── models/
│   │   ├── base_catalogue.py     # Базовая модель справочника
│   │   └── dummy.py              # Пример справочника
│   ├── factories/
│   │   └── catalogues.py         # Фабрика тестовых данных
│   └── catalogue_registry.py     # Реестр всех справочников
├── schemas/
│   ├── catalogues.py             # Схемы справочников
│   ├── enums.py                  # Enum'ы для справочников
│   └── article_schemas.py        # Схемы для статей (пример)
├── services/
│   └── catalogue_service.py      # Сервис управления справочниками
├── utils/
│   └── generate_sql_for_catalogues.py # Генерация SQL для инициализации
└── README.md                     # Документация модуля
```

## Базовая модель справочника

### BaseCatalogueModel
Все справочники наследуются от базовой модели:
```python
class BaseCatalogueModel(Base):
    __abstract__ = True
    
    key: Mapped[str] = mapped_column(String(100), unique=True)   # Ключ
    value: Mapped[str] = mapped_column(String(100), unique=True) # Значение
```

### Пример справочника
```python
class StatusCatalogueModel(BaseCatalogueModel):
    __tablename__ = "catalogue_status"
```

## Схемы данных

### BaseCatalogueSchema
Базовая схема для справочников:
```python
class BaseCatalogueSchema(BaseSchema):
    key: str        # Программный ключ (например, "active")
    value: str      # Человекочитаемое значение (например, "Активный")
```

### APICatalogueSchema
Схема для API с автоматическим маршрутом:
```python
class APICatalogueSchema(BaseCatalogueSchema):
    id: UUID
    route: str | None = None    # Автоматически генерируемый маршрут
    
    @model_validator(mode="before")
    def get_route_from_sql_tablename(self) -> Self:
        # catalogue_table_name -> /catalogues/table-name/
        tablename = self.__tablename__
        route_path = tablename.replace("catalogue_", "catalogues/").replace("_", "-")
        self.route = f"/{route_path}/"
        return self
```

## Автоматическая генерация API

### Динамические эндпоинты
Модуль автоматически создает REST эндпоинты для всех справочников:

```python
def generate_catalogue_endpoint(name: str) -> Callable:
    async def endpoint(
        account: Annotated[get_account_from_token, Depends()],
        service: CatalogueService = Depends(get_service(CatalogueService)),
    ):
        try:
            return await service.get_catalogue_by_name(name)
        except ValueError:
            raise HTTPException(status_code=404, detail="Catalogue not found")
    return endpoint

# Автоматическая регистрация всех справочников
for path_name in catalogue_registry.keys():
    router.add_api_route(
        f"/{path_name}/",
        generate_catalogue_endpoint(path_name),
        response_model=list[CatalogueSchema],
        methods=["GET"],
        name=f"Get catalogue: {path_name}",
    )
```

### Реестр справочников
```python
def generate_catalogue_registry():
    registry = {}
    
    for name, obj in inspect.getmembers(models):
        if (
            inspect.isclass(obj)
            and issubclass(obj, BaseCatalogueModel)
            and obj is not BaseCatalogueModel
        ):
            tablename = getattr(obj, "__tablename__", "")
            if tablename.startswith(CATALOGUE_PREFIX):
                key = tablename[len(CATALOGUE_PREFIX):].replace("_", "-")
                registry[key] = obj
    
    return registry
```

## Правила именования

### Строгие правила для справочников

#### Имена таблиц
- **Префикс**: `catalogue_`
- **Формат**: `catalogue_table_name`
- **Пример**: `catalogue_user_status`

#### API маршруты
- **Формат**: `/catalogues/table-name/`
- **Преобразование**: `_` → `-`
- **Пример**: `catalogue_user_status` → `/catalogues/user-status/`

#### Модели классов
```python
class UserStatusCatalogueModel(BaseCatalogueModel):
    __tablename__ = "catalogue_user_status"
```

## Сервис справочников

### CatalogueService
```python
class CatalogueService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self.catalogue = GeneralCatalogueCRUD(self.session)

    async def get_catalogue_by_name(self, name: str):
        model_class = catalogue_registry.get(name)
        if not model_class:
            raise ValueError(f"Catalogue '{name}' not found")
        return await self.catalogue.get_catalogue_by_model(model_class)
```

### GeneralCatalogueCRUD
Универсальный CRUD для всех справочников:
```python
class GeneralCatalogueCRUD(BaseCRUD[BaseCatalogueSchema, APICatalogueSchema, Base]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_catalogue_by_model(self, model_class: type[Base]):
        self._table = model_class
        res = await self.get_all()
        self._table = None
        return res
```

## Примеры справочников

### Статусы пользователей
```python
USER_STATUS_DATA = {
    "catalogue_user_status": [
        {"key": "active", "value": "Активный"},
        {"key": "inactive", "value": "Неактивный"},
        {"key": "blocked", "value": "Заблокирован"},
        {"key": "pending", "value": "На модерации"},
    ]
}
```

### Страны
```python
COUNTRIES_DATA = {
    "catalogue_countries": [
        {"key": "ru", "value": "Россия"},
        {"key": "us", "value": "США"},
        {"key": "uk", "value": "Великобритания"},
        {"key": "de", "value": "Германия"},
    ]
}
```

## Инициализация данных

### Фабрика данных
```python
CATALOGUES_DATA = {
    "catalogue_test": [
        {"key": "test", "value": "Тест"},
    ],
}
```

### Генерация SQL
```python
def generate_insert_sql(data: CATALOGUE_DICT) -> str:
    insert_template = 'INSERT INTO {table_name} ("key", value) VALUES '
    values_row = "\n('{key}', '{value}'),"

    for table_name in data:
        full_query = insert_template.format(table_name=table_name)
        
        for table_data in data[table_name]:
            full_query += values_row.format(
                key=table_data["key"],
                value=table_data["value"],
            )
        
        yield full_query.rstrip(",") + ";"
```

### Очистка данных
```python
def generate_truncate_sql(data: CATALOGUE_DICT) -> str:
    query_template = 'TRUNCATE table "{table_name}" CASCADE'
    
    for table_name in data:
        yield query_template.format(table_name=table_name)
```

## Использование API

### Получение справочника
```http
GET /catalogues/user-status/
Authorization: Bearer <jwt_token>
```

Ответ:
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "key": "active",
      "value": "Активный",
      "route": "/catalogues/user-status/"
    },
    {
      "id": "uuid", 
      "key": "inactive",
      "value": "Неактивный",
      "route": "/catalogues/user-status/"
    }
  ]
}
```

### Список всех справочников
Автоматически генерируются эндпоинты для всех справочников в системе. Список доступен в Swagger документации.

## Добавление нового справочника

### 1. Создание модели
```python
# В models/__init__.py
from .user_roles import UserRolesCatalogueModel

# В models/user_roles.py  
class UserRolesCatalogueModel(BaseCatalogueModel):
    __tablename__ = "catalogue_user_roles"
```

### 2. Добавление данных
```python
# В factories/catalogues.py
USER_ROLES_DATA = {
    "catalogue_user_roles": [
        {"key": "admin", "value": "Администратор"},
        {"key": "moderator", "value": "Модератор"},
        {"key": "user", "value": "Пользователь"},
    ]
}

# Добавить в CATALOGUES_DATA
CATALOGUES_DATA.update(USER_ROLES_DATA)
```

### 3. Создание миграции
```bash
python manage.py db --migrate
```

### 4. Автоматическое API
После рестарта приложения автоматически станет доступен эндпоинт:
`GET /catalogues/user-roles/`

## Интеграция с фронтендом

### Автоматический маршрут
Каждый справочник содержит поле `route` для упрощения интеграции с фронтендом:

```typescript
interface CatalogueItem {
  id: string;
  key: string;
  value: string; 
  route: string;  // "/catalogues/user-status/"
}

// Использование
const userStatuses = await api.get<CatalogueItem[]>(catalogue.route);
```

### Кэширование на фронтенде
```typescript
class CatalogueCache {
  private cache = new Map<string, CatalogueItem[]>();
  
  async getCatalogue(route: string): Promise<CatalogueItem[]> {
    if (!this.cache.has(route)) {
      const data = await api.get<CatalogueItem[]>(route);
      this.cache.set(route, data);
    }
    return this.cache.get(route)!;
  }
}
```

## Конфигурация
Модуль не требует дополнительных настроек - все справочники автоматически регистрируются при старте приложения.

## Интеграция с другими модулями

### Auth Module
- Статусы пользователей
- Роли и права доступа
- Типы учетных записей

### Chat Module
- Типы чатов
- Статусы сообщений
- Роли участников

## Планы развития

### Краткосрочные планы
- **Иерархические справочники** (parent-child связи)
- **Кэширование** справочников в Redis

### Долгосрочные планы
- **Административный интерфейс** для управления справочниками
- **Аудит изменений** справочных данных
- **Импорт/экспорт** справочников
- **API для создания** новых справочников через интерфейс
- **Права доступа** к отдельным справочникам
- **Валидация связанных данных** при изменении справочников

## Важные особенности

### Безопасность
- Все справочники требуют авторизации
- Только чтение данных (нет API для изменения)
- Валидация входных параметров

### Производительность  
- Справочники загружаются один раз при старте
- Минимальное количество SQL запросов
- Эффективная регистрация через introspection

### Масштабируемость
- Автоматическое добавление новых справочников
- Унифицированная архитектура
- Простота расширения функциональности
