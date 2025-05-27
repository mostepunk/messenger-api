# Base Module
Базовый модуль, предоставляющий общие компоненты и абстракции для всех остальных модулей проекта. Включает базовые классы для CRUD операций, схем данных, сервисов и обработки ошибок.

## Назначение модуля
Base Module решает задачи унификации и переиспользования кода:

- **Базовые CRUD операции** для работы с базой данных
- **Общие схемы данных** и валидация
- **Стандартизация ошибок** и их обработка
- **Пагинация** для списочных запросов
- **Базовые сервисы** для бизнес-логики
- **Типы данных** с валидацией (email, телефон, пароль)

## Структура модуля

```
base_module/
├── api/
│   └── __init__.py              # Пустой роутер (заглушка)
├── db/
│   ├── cruds/
│   │   └── base_crud.py         # Базовый CRUD класс
│   ├── models/
│   │   └── base.py              # Базовая модель SQLAlchemy
│   └── errors.py                # Исключения для БД
├── schemas/
│   ├── base.py                  # Базовые Pydantic схемы
│   ├── customs.py               # Кастомные типы данных
│   ├── pagination.py            # Схемы пагинации
│   └── erros_schemas.py         # Схемы ошибок
├── services/
│   └── base_service.py          # Базовый сервис
├── errors.py                    # Базовые исключения
└── README.md                    # Документация модуля
```

## Базовые модели

### Base (SQLAlchemy модель)
Базовая модель для всех таблиц:
```python
class Base(AsyncAttrs, DeclarativeBase):
    id: UUID                    # Первичный ключ
    created_at: datetime        # Время создания
    updated_at: datetime        # Время обновления
    
    async def save(session)     # Сохранение в БД
    async def delete(session)   # Удаление из БД
```

Возможности:
- **Автогенерация UUID** для первичного ключа
- **Автоматические временные метки** создания и обновления
- **Асинхронные методы** для сохранения и удаления
- **Работа с relationships** через awaitable_attrs

## Базовые схемы

### BaseSchema (Pydantic)
Базовая схема для всех API моделей:
```python
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,    # автоматический camelCase
        populate_by_name=True,       # поддержка snake_case и camelCase
        str_strip_whitespace=True,   # автоматическая обрезка пробелов
        use_enum_values=True,        # использование значений enum
        from_attributes=True         # создание из SQLAlchemy моделей
    )
```

### BaseDB
Схема для моделей из базы данных:
```python
class BaseDB(BaseSchema):
    id: UUID
    created_at: datetime  
    updated_at: datetime
```

### Кастомные типы данных

#### EmailStr
Валидация email адресов:
```python
class EmailStr(BaseValidator):
    # Проверка на соответствие email паттерну
    # Автоматическая обрезка пробелов
```

#### PasswordStr  
Валидация паролей:
```python
class PasswordStr(BaseValidator):
    # Минимум 8 символов
    # Наличие строчных и заглавных букв
    # Поддержка русских символов
```

#### PhoneStr
Валидация телефонных номеров:
```python
class PhoneStr(BaseValidator):
    # Использует библиотеку phonenumbers
    # Поддержка международного формата
    # Валидация для региона RU
```

## Базовый CRUD

### BaseCRUD
Универсальный класс для операций с базой данных:

```python
class BaseCRUD(Generic[S_in, S_out, T]):
    _in_schema: type[S_in]      # Схема для входных данных
    _out_schema: type[S_out]    # Схема для выходных данных  
    _table: type[T]             # SQLAlchemy модель
```

#### Основные методы:

**Создание:**
```python
async def add(self, in_schema: S_in) -> S_out
async def add_many(self, in_schema: list[S_in]) -> list[S_out]
```

**Чтение:**
```python
async def get_all(self) -> list[S_out]
async def get_by_id(self, item_uuid: UUID) -> S_out
async def get_by_ids(self, ids: list[UUID]) -> list[S_out]
```

**Обновление:**
```python
async def update(self, item_uuid: UUID, data: dict | S_in) -> S_out
async def update_many(self, values: list[dict])
```

**Удаление:**
```python
async def delete(self, item_uuid: UUID)
async def delete_many(self, ids: list[UUID])
```

**Пагинация:**
```python
async def paginated_select(
    self, query: select, limit: int, offset: int
) -> tuple[int, ScalarResult]
```

### Особенности реализации

- **Автоматическая валидация** входных и выходных данных
- **Пакетные операции** для производительности
- **Chunked обработка** больших списков
- **Обработка relationships** через awaitable_attrs
- **Унифицированная обработка ошибок**

## Пагинация

### PaginationParams
Параметры для пагинации списков:
```python
class PaginationParams(BaseSchema):
    limit: int | None = None     # Количество элементов
    offset: int | None = None    # Смещение (автоматически -1)
```

### Paginator
Результат с пагинацией:
```python
class Paginator(PaginationParams):
    total_count: int            # Общее количество элементов
```

Пример использования:
```python
@router.get("/items/")
async def get_items(
    pagination: Annotated[PaginationParams, Depends()]
):
    total, items = await crud.paginated_select(
        query, pagination.limit, pagination.offset
    )
    return {"total_count": total, "items": items}
```

## Базовый сервис

### BaseService
Базовый класс для бизнес-логики:
```python
class BaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
```

Использование:
```python
class UserService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.user_crud = UserCRUD(session)
    
    async def create_user(self, data: UserCreate) -> User:
        user = await self.user_crud.add(data)
        await self.session.commit()
        return user
```

## Система ошибок

### Базовые исключения

#### BaseAppException
Родительский класс для всех ошибок приложения:
```python
class BaseAppException(HTTPException):
    status_code = 500
    detail = "Unknown Error"
    code = ErrorCode.unknown
```

#### BaseDBError
Ошибки базы данных:
```python
class BaseDBError(BaseAppException):
    status_code = 503
    detail = "DataBase error" 
    code = ErrorCode.database_error
```

#### ItemNotFoundError
Элемент не найден:
```python
class ItemNotFoundError(BaseDBError):
    status_code = 404
    detail = "Item not found"
    code = ErrorCode.not_found
```

#### ItemAlreadyExistsError
Элемент уже существует:
```python
class ItemAlreadyExistsError(BaseDBError):
    status_code = 409
    detail = "Item already exists"
```

### Схемы ошибок

#### ErrorResponseSchema
Стандартный формат ошибки:
```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "Item not found"
  }
}
```

#### SuccessResponseSchema  
Стандартный формат успешного ответа:
```json
{
  "status": "success", 
  "data": {...}
}
```

## Утилиты

### Enum с описанием
```python
class StrEnum(str, Enum):
    """Enum с поддержкой описания"""
    
    def __new__(cls, value: str, phrase: str = None):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        return obj
    
    @property
    def choices(cls) -> list[SelectEnum]:
        # Возвращает список для select-ов
```

### Функция to_camel
Автоматическое преобразование snake_case в camelCase:
```python
def to_camel(snake_str: str) -> str:
    # user_name -> userName
    # created_at -> createdAt
```

## Тестирование

Base Module предоставляет базовые компоненты для тестирования:

- **Базовые фикстуры** для сессий БД
- **Моки CRUD операций** 
- **Фабрики тестовых данных**
- **Утилиты валидации** схем

## Конфигурация

Настройки базового модуля:
```bash
# Размер чанков для пакетных операций
PG_SERVER_CHUNK_SIZE=1000

# Настройки валидации
AUTH_EMAIL_PATTERN=^(?:[^@ \t\r\n]+)@(?:[^@ \t\r\n]+\.)+[^@ \t\r\n.]{2,}$
AUTH_PASSWORD_PATTERN=^(?=.*[a-zа-яА-Я])(?=.*[A-Zа-яА-Я]).{8,}$
AUTH_EMAIL_STRIP_ENABLED=true
AUTH_PASSWORD_STRIP_ENABLED=true
```

## Использование в других модулях

### Наследование CRUD
```python
from app.modules.base_module.db.cruds.base_crud import BaseCRUD

class UserCRUD(BaseCRUD[UserCreate, UserDB, UserModel]):
    _in_schema = UserCreate
    _out_schema = UserDB  
    _table = UserModel
    
    def __init__(self, session: AsyncSession):
        self.session = session
```

### Наследование схем
```python
from app.modules.base_module.schemas.base import BaseSchema, BaseDB

class UserSchema(BaseSchema):
    name: str
    email: EmailStr

class UserDBSchema(UserSchema, BaseDB):
    pass  # Автоматически добавляются id, created_at, updated_at
```

### Наследование сервисов
```python
from app.modules.base_module.services.base_service import BaseService

class UserService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.crud = UserCRUD(session)
```

## Примеры использования

### Создание полного CRUD
```python
# Модель
class ArticleModel(Base):
    __tablename__ = "articles"
    title: Mapped[str]
    content: Mapped[str]

# Схемы
class ArticleCreate(BaseSchema):
    title: str
    content: str

class ArticleDB(ArticleCreate, BaseDB):
    pass

# CRUD
class ArticleCRUD(BaseCRUD[ArticleCreate, ArticleDB, ArticleModel]):
    _in_schema = ArticleCreate
    _out_schema = ArticleDB
    _table = ArticleModel

# API
@router.post("/", response_model=ArticleDB)
async def create_article(
    data: ArticleCreate,
    crud: ArticleCRUD = Depends(get_crud(ArticleCRUD))
):
    return await crud.add(data)
```

### Кастомная валидация
```python
class CustomValidator(BaseValidator):
    @classmethod
    def _validate(cls, value: str) -> str:
        if not value.startswith("PREFIX_"):
            raise ValueError("Value must start with PREFIX_")
        return value

class MySchema(BaseSchema):
    custom_field: CustomValidator
```

## Планы развития

- **Soft delete** поддержка в базовой модели
- **Audit trail** для отслеживания изменений
- **Кэширование** на уровне CRUD
- **Bulk operations** с лучшей производительностью
- **Фильтрация и сортировка** в базовом CRUD
- **Валидация на уровне БД** через constraints
