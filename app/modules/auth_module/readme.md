# Auth Module
Модуль авторизации и аутентификации пользователей с поддержкой JWT токенов, регистрации, подтверждения email и управления сессиями.

## Назначение модуля
Auth Module решает все задачи, связанные с управлением пользователями и их аутентификацией:

- **Регистрация** новых пользователей с подтверждением email
- **Аутентификация** через email/пароль
- **Авторизация** с помощью JWT токенов
- **Управление сессиями** пользователей
- **Восстановление пароля** через email
- **Multi-device поддержка** (несколько устройств на одного пользователя)

## Структура модуля

```
auth_module/
├── api/
│   └── routes/
│       └── auth.py              # API эндпоинты авторизации
├── db/
│   ├── cruds/
│   │   ├── account_crud.py      # CRUD для аккаунтов
│   │   └── account_session_crud.py # CRUD для сессий
│   ├── models/
│   │   └── account.py           # Модели аккаунта и сессий
│   └── factories/
│       └── account.py           # Фабрика тестовых данных
├── schemas/
│   ├── account.py               # Схемы аккаунта
│   ├── account_session.py       # Схемы сессий
│   ├── token.py                 # Схемы токенов
│   └── auth_form.py             # Формы для Swagger
├── services/
│   └── auth_service.py          # Бизнес-логика авторизации
├── dependencies/
│   ├── jwt_decode.py            # JWT декодирование и валидация
│   ├── token.py                 # Создание токенов
│   └── errors.py                # Исключения токенов
├── utils/
│   ├── oauth.py                 # OAuth2 схема для Swagger
│   ├── password.py              # Хеширование паролей
│   ├── errors.py                # Исключения авторизации
│   └── const.py                 # Константы
└── tests/                       # Тесты модуля
```

## Основные компоненты

### Модели данных

#### AccountModel
Основная модель пользователя:
- `email` - уникальный email
- `password` - хешированный пароль  
- `is_confirmed` - подтвержден ли email
- `confirmation_token` - токен для подтверждения
- `profile_id` - связь с профилем пользователя

#### AccountSessionModel
Модель сессий пользователя:
- `refresh_token` - токен обновления
- `access_token` - токен доступа
- `fingerprint` - отпечаток устройства
- `account_id` - связь с аккаунтом

### API Эндпоинты

#### POST /accounts/sign-up/
Регистрация нового пользователя
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### POST /accounts/sign-in/
Вход в систему
```json
{
  "email": "user@example.com", 
  "password": "securePassword123",
  "fingerprint": "device-uuid"
}
```

#### POST /accounts/sign-out/
Выход из системы (удаление refresh токена)

#### GET /accounts/me/
Получение информации о текущем пользователе

#### POST /accounts/email/confirm/
Подтверждение email по токену

#### POST /accounts/password/reset/
Запрос на сброс пароля

#### POST /accounts/token/refresh/
Обновление access токена

### Система токенов

Модуль использует трехуровневую систему JWT токенов:

1. **Access Token** (30 минут) - для API запросов
2. **Refresh Token** (60 дней) - для обновления access токена  
3. **Confirmation Token** (2 дня) - для подтверждения email/сброса пароля

### Безопасность

- **Хеширование паролей** с помощью bcrypt
- **Валидация токенов** с проверкой в базе данных
- **Fingerprint защита** от кражи refresh токенов
- **Rate limiting** через дедупликацию запросов
- **Secure cookies** для refresh токенов

## Основные сценарии использования

### Регистрация пользователя

1. Пользователь отправляет email/пароль
2. Создается неподтвержденный аккаунт
3. Генерируется confirmation токен
4. Отправляется email с ссылкой подтверждения
5. Пользователь переходит по ссылке и подтверждает email
6. Создается сессия, возвращаются токены

### Аутентификация

1. Пользователь отправляет email/пароль + fingerprint
2. Проверяется пароль и статус подтверждения
3. Создается или обновляется сессия для устройства
4. Возвращается access токен + refresh в cookie

### Обновление токенов

1. Клиент отправляет refresh токен из cookie
2. Проверяется валидность и соответствие fingerprint
3. Генерируются новые access и refresh токены
4. Старые токены инвалидируются

### Восстановление пароля

1. Пользователь запрашивает сброс по email
2. Генерируется confirmation токен
3. Отправляется email со ссылкой
4. Пользователь подтверждает токен
5. Устанавливается новый пароль

## Тестирование

Модуль включает комплексные тесты:

- **Unit тесты** сервисов и CRUD
- **Integration тесты** API эндпоинтов
- **Security тесты** валидации токенов
- **Email flow тесты** подтверждения и сброса

## Конфигурация

Основные настройки в переменных окружения:

```bash
# JWT настройки
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=60

# Email валидация
AUTH_EMAIL_PATTERN=^(?:[^@ \t\r\n]+)@(?:[^@ \t\r\n]+\.)+[^@ \t\r\n.]{2,}$
AUTH_PASSWORD_PATTERN=^(?=.*[a-zа-яА-Я])(?=.*[A-Zа-яА-Я]).{8,}$
```

## Интеграция с другими модулями

### Chat Module
- Аутентификация WebSocket соединений
- Получение профиля пользователя для чатов

### Notify Module  
- Отправка email подтверждений
- Уведомления о сбросе пароля

## Примеры использования

### Dependency Injection
```python
from app.modules.auth_module.dependencies.jwt_decode import get_account_from_token

@router.get("/protected/")
async def protected_endpoint(
    account: Annotated[get_account_from_token, Depends()]
):
    return {"user_id": account.id}
```

### WebSocket аутентификация
```python
from app.modules.auth_module.dependencies.jwt_decode import authenticate_websocket_user

async def websocket_endpoint(websocket: WebSocket):
    token = await websocket.receive_text()
    user = await authenticate_websocket_user(token)
    if not user:
        await websocket.close(code=1008)
```

## Обработка ошибок

Модуль предоставляет структурированные исключения:

- `CredentialsError` - неверные учетные данные
- `AccountAlreadyExists` - аккаунт уже существует
- `AccountNotExists` - аккаунт не найден
- `TokenExpiredError` - токен истек
- `InvalidTokenError` - невалидный токен

## Планы развития
- Двухфакторная аутентификация (2FA)
- OAuth2 интеграция (Google, GitHub)
- Аудит логирование действий пользователей
- Rate limiting на уровне пользователя
- Блокировка подозрительных аккаунтов
