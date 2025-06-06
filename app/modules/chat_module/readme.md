# Chat Module
Основной модуль мессенджера, реализующий real-time обмен сообщениями через WebSocket, управление чатами, профилями пользователей и предотвращение дублирования сообщений.

## Назначение модуля
Chat Module - это сердце мессенджера, решающий ключевые задачи:

- **Real-time коммуникация** через WebSocket соединения
- **Управление чатами** (создание, редактирование, удаление)
- **Отправка сообщений** с гарантией доставки
- **Статусы прочтения** для групповых и личных чатов
- **История сообщений** с пагинацией
- **Предотвращение дублирования** при параллельной отправке
- **Multi-device поддержка** (одновременное подключение с нескольких устройств)
- **Управление участниками** групповых чатов

## Структура модуля

```
chat_module/
├── api/
│   └── routes/
│       ├── chats.py             # REST API для чатов
│       └── websocket.py         # WebSocket эндпоинты
├── db/
│   ├── cruds/
│   │   ├── chat_crud.py         # CRUD операции с чатами
│   │   ├── message_crud.py      # CRUD операции с сообщениями
│   │   └── profile_crud.py      # CRUD операции с профилями
│   ├── models/
│   │   ├── chat.py              # Модели чатов и сообщений
│   │   └── profile.py           # Модели профилей
│   └── factories/
│       ├── chat.py              # Фабрика тестовых чатов
│       └── profile.py           # Фабрика тестовых профилей
├── schemas/
│   ├── chat_schemas.py          # Схемы чатов
│   ├── message_schema.py        # Схемы сообщений
│   └── profile_schemas.py       # Схемы профилей
├── services/
│   ├── chat_service.py          # Бизнес-логика чатов
│   ├── websocket_service.py     # Обработка WebSocket соединений
│   └── deduplication_service.py # Предотвращение дублирования
├── websocket/
│   └── connection_manager.py    # Менеджер WebSocket соединений
├── resources/
│   └── html_chat.py             # HTML клиент для тестирования
├── errors.py                    # Исключения модуля
└── tests/                       # Тесты модуля
    ├── chat_service/            # Тесты сервиса чатов
    └── websockets/              # Тесты WebSocket функциональности
```

## Модели данных

### ChatModel
Основная модель чата:
- `name` - название чата
- `description` - описание чата
- `owner_id` - владелец чата
- `members` - участники чата (many-to-many)

### MessageModel  
Модель сообщения:
- `chat_id` - чат, в который отправлено
- `text` - текст сообщения
- `sender_id` - отправитель
- `sent_at` - время отправки
- `read_at` - время прочтения (для 1-to-1 чатов)
- `read_statuses` - статусы прочтения (для групповых чатов)

### ProfileModel
Модель профиля пользователя:
- `first_name`, `last_name`, `middle_name` - ФИО
- `username` - никнейм
- `chats` - список чатов пользователя

### MessageReadStatusModel
Статусы прочтения для групповых чатов:
- `message_id` - сообщение
- `profile_id` - пользователь
- `read_at` - время прочтения

## REST API

### Управление чатами

#### GET /chats/
Получить список чатов пользователя
```json
[
  {
    "id": "uuid",
    "name": "Название чата",
    "description": "Описание",
    "owner": {...}
  }
]
```

#### POST /chats/
Создать новый чат
```json
{
  "name": "Новый чат",
  "description": "Описание чата",
  "members": ["profile_id_1", "profile_id_2"]
}
```

#### GET /chats/{chat_id}/
Получить детальную информацию о чате

#### PUT /chats/{chat_id}/
Обновить чат (только владелец)

#### DELETE /chats/{chat_id}/
Удалить чат (только владелец)

#### GET /chats/{chat_id}/history/
Получить историю сообщений с пагинацией

## 🔌 WebSocket API

### Подключение
```
WS /chats/{chat_id}/ws
```

### Сообщения аутентификации
```json
{
  "type": "auth",
  "token": "jwt_access_token"
}
```

### Типы сообщений

#### Отправка сообщения
```json
{
  "type": "send_message",
  "text": "Текст сообщения"
}
```

#### Индикатор печати
```json
{
  "type": "typing",
  "is_typing": true
}
```

#### Отметка прочтения
```json
{
  "type": "mark_read",
  "last_read_message_id": "uuid"
}
```

#### Отметка одного сообщения
```json
{
  "type": "mark_single_read", 
  "message_id": "uuid"
}
```

#### Покидание чата
```json
{
  "type": "leave_chat"
}
```

#### Запрос истории
```json
{
  "type": "get_chat_history",
  "limit": 20,
  "offset": 0
}
```

### Входящие события

#### Новое сообщение
```json
{
  "type": "new_message",
  "message": {
    "id": "uuid",
    "text": "Текст",
    "sender": {...},
    "sent_at": "2025-01-01T12:00:00Z"
  }
}
```

#### Пользователь присоединился
```json
{
  "type": "user_joined",
  "user_id": "uuid",
  "chat_id": "uuid"
}
```

#### Сообщения прочитаны
```json
{
  "type": "messages_read",
  "read_by": "uuid",
  "message_ids": ["uuid1", "uuid2"],
  "read_count": 2
}
```

## Ключевые сервисы

### WebsocketService
Основной сервис для обработки WebSocket соединений:

- **Аутентификация** пользователей по JWT
- **Автоматическое присоединение** к чату после аутентификации
- **Обработка входящих сообщений** по типам
- **Отправка истории** чата при подключении
- **Управление статусами** прочтения

### ConnectionManager
Менеджер WebSocket соединений:

- **Multi-device поддержка** одного пользователя
- **Управление чат-комнатами** и участниками
- **Рассылка сообщений** в чаты и персонально
- **Отслеживание онлайн статуса** пользователей
- **Graceful отключение** соединений

### DeduplicationService  
Сервис предотвращения дублирования:

- **Блокировки на уровне пользователя** в чате
- **Кэширование отправленных сообщений** с TTL
- **Защита от спама** с минимальным интервалом
- **Нормализация текста** сообщений

### ChatService
Бизнес-логика управления чатами:

- **CRUD операции** с чатами
- **Управление участниками** групповых чатов
- **Проверка прав доступа** владельца
- **Получение истории** с пагинацией

## Особенности реализации

### Multi-device поддержка
- Один пользователь может подключаться с нескольких устройств
- Уведомления о входе/выходе отправляются только при полном подключении/отключении
- Каждое устройство управляется независимо

### Предотвращение дублирования
- Асинхронные блокировки на комбинацию (пользователь + чат)
- Кэширование хешей сообщений с временными метками
- Автоматическая очистка устаревших записей

### Статусы прочтения
- Для личных чатов (1-to-1): простое поле `read_at` в сообщении
- Для групповых чатов: отдельная таблица `message_read_status`
- Пакетная отметка сообщений "до определенного ID"

### Масштабируемость
- Асинхронная обработка всех операций
- Эффективные SQL запросы с joinedload
- Пагинация для истории сообщений
- Индексы на часто используемые поля

## Тестирование
Модуль включает обширное покрытие тестами:

### Unit тесты
- **ChatService** - тесты бизнес-логики чатов
- **WebsocketService** - тесты обработки WebSocket сообщений  
- **DeduplicationService** - тесты предотвращения дублирования
- **ConnectionManager** - тесты управления соединениями

### Integration тесты
- **Полный flow** создания чата и отправки сообщений
- **Multi-device сценарии** подключения
- **Конкурентная отправка** сообщений
- **Транзакционность** операций

### WebSocket тесты
- **Connection lifecycle** (подключение → аутентификация → отключение)
- **Message routing** между участниками чата
- **Error handling** при некорректных данных
- **Concurrent connections** множественных пользователей

## HTML Test Client
Модуль включает готовый HTML клиент для тестирования WebSocket функциональности:

- Подключение к чату по JWT токену
- Отправка и получение сообщений
- Индикаторы печати
- История сообщений
- Статусы подключения

Доступен по адресу: `GET /chats/html`

## Конфигурация

Основные настройки в переменных окружения:

```bash
# Настройки чата
CHAT_CACHE_TTL_SECONDS=60           # TTL кэша дедупликации
CHAT_MIN_MESSAGE_INTERVAL=1.0       # Минимальный интервал между сообщениями
```

## Примеры использования

### Создание чата через API
```python
async def create_group_chat():
    chat_data = CreateChatSchema(
        name="Рабочий чат",
        description="Обсуждение проекта",
        members=[user1_id, user2_id, user3_id]
    )
    
    chat = await chat_service.create_chat(owner_id, chat_data)
    return chat
```

### WebSocket обработка сообщений
```python
async def handle_websocket_message(message_data, user_id, chat_id):
    if message_data["type"] == "send_message":
        text = message_data["text"].strip()
        
        # Проверка дедупликации
        is_allowed, reason = await dedup_service.check_and_prevent_duplicate(
            user_id, chat_id, text
        )
        
        if is_allowed:
            # Сохранение в БД
            message = await message_crud.add({
                "chat_id": chat_id,
                "sender_id": user_id, 
                "text": text,
                "sent_at": datetime.utcnow()
            })
            
            # Рассылка участникам
            await connection_manager.broadcast_to_chat({
                "type": "new_message",
                "message": message.model_dump()
            }, chat_id)
```

### Отметка сообщений как прочитанных
```python
async def mark_messages_read(chat_id, user_id, last_message_id):
    # Отметить все сообщения до указанного ID
    read_ids = await message_crud.mark_messages_read_by_last_id(
        chat_id, user_id, last_message_id
    )
    
    if read_ids:
        # Уведомить участников чата
        await connection_manager.broadcast_to_chat({
            "type": "messages_read",
            "read_by": str(user_id),
            "message_ids": [str(mid) for mid in read_ids],
            "read_count": len(read_ids)
        }, chat_id)
```

## Интеграция с другими модулями

### Auth Module
- Аутентификация WebSocket соединений через JWT
- Получение информации о пользователях
- Проверка прав доступа к чатам

### Notify Module
- Пуш-уведомления о новых сообщениях (планируется)
- Email уведомления при упоминаниях (планируется)

## Обработка ошибок

Модуль предоставляет специализированные исключения:

- `ChatNotFound` - чат не найден
- `AccessDenied` - нет прав доступа
- `MembersNotFound` - участники не найдены
- `ProhibitedToModifyChat` - нет прав на изменение

## Мониторинг и статистика

### ConnectionManager статистика
```python
stats = connection_manager.get_chat_stats(chat_id)
# {
#   "users": 5,
#   "connections": 8, 
#   "users_with_multiple_devices": 2
# }
```

### DeduplicationService статистика
```python
stats = dedup_service.get_stats()
# {
#   "cached_messages": 150,
#   "active_locks": 5,
#   "cache_ttl": 60,
#   "min_interval": 1.0
# }
```

## Планы развития
- **Медиа сообщения** (изображения, файлы, голосовые)
- **Реакции на сообщения** (эмодзи)
- **Редактирование и удаление** сообщений
- **Пересылка сообщений** между чатами
- **Поиск по истории** сообщений
- **Уведомления о упоминаниях** (@username)
- **Роли участников** в групповых чатах (админ, модератор)
- **Приватные чаты** с end-to-end шифрованием
- **Боты и интеграции** с внешними сервисами
- **Голосовые и видео звонки** через WebRTC

## WebSocket протокол
### Жизненный цикл соединения

1. **Подключение** к `/chats/{chat_id}/ws`
2. **Аутентификация** отправкой JWT токена
3. **Автоматическое присоединение** к чату (если пользователь участник)
4. **Получение истории** последних сообщений
5. **Обмен сообщениями** в real-time
6. **Graceful отключение** при закрытии соединения

### Коды закрытия WebSocket
- `1008` - Authentication failed / Access denied / Chat not found
- `1011` - Internal server error

### Обработка ошибок в WebSocket

Все ошибки отправляются в формате:
```json
{
  "type": "error",
  "message": "Описание ошибки"
}
```

## Производительность

### Оптимизации

- **Connection pooling** для базы данных
- **Eager loading** связанных данных через joinedload
- **Индексы** на chat_id, sender_id, sent_at
- **Пагинация** для больших списков сообщений
- **Кэширование** частых запросов

### Ограничения

- Максимум **1000 участников** в групповом чате
- Максимум **4000 символов** в сообщении  
- Минимум **1 секунда** между сообщениями от одного пользователя
- TTL кэша дедупликации **60 секунд**

## Разработка и отладка

### Логирование
Модуль использует структурированное логирование:
- `INFO` - подключения/отключения пользователей
- `DEBUG` - детали WebSocket сообщений (только в DEV/LOCAL)
- `WARNING` - блокировки дублирующихся сообщений
- `ERROR` - ошибки обработки сообщений

### Отладка WebSocket
Используйте встроенный HTML клиент или инструменты разработчика браузера для тестирования WebSocket соединений.

### Профилирование
Для анализа производительности используйте:
```python
# Статистика менеджера соединений
print(connection_manager.get_chat_stats(chat_id))

# Статистика дедупликации  
print(dedup_service.get_stats())
```
