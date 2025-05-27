# Notify Module
Модуль уведомлений, обеспечивающий отправку email сообщений с поддержкой шаблонов, вложений и логирования доставки.

## Назначение модуля
Notify Module решает задачи доставки уведомлений пользователям:

- **Email уведомления** через SMTP
- **Шаблонизация писем** с динамическими данными
- **Поддержка вложений** (изображения, документы)
- **Логирование отправок** и ошибок
- **Множественные получатели** в одном письме
- **HTML письма** с встроенными изображениями
- **Фоновая отправка** через BackgroundTasks

## Структура модуля

```
notify_module/
├── api/
│   └── routes/
│       └── router.py            # API эндпоинты (заглушка)
├── db/
│   ├── cruds/
│   │   └── model_crud.py        # CRUD заглушка
│   ├── models/
│   │   └── notify_models.py     # Модели шаблонов и логов
│   └── factories/
│       └── factory.py           # Фабрика тестовых шаблонов
├── schemas/
│   └── notify_schemas.py        # Схемы уведомлений
├── services/
│   └── notification_service.py  # Сервис отправки уведомлений
├── errors.py                    # Исключения модуля
└── README.md                    # Документация
```

## Модели данных

### TemplateModel
Шаблон уведомления:
- `type` - тип уведомления (email, sms, push)
- `code` - уникальный код шаблона
- `subject` - тема письма
- `body` - HTML содержимое с Jinja2 переменными
- `attachments` - связанные вложения

### AttachmentModel  
Вложение к шаблону:
- `base64` - содержимое файла в base64
- `filename` - имя файла
- `cid` - Content-ID для встраивания в HTML
- `template_id` - связь с шаблоном

### NotificationLogModel
Лог отправки уведомления:
- `template_id` - использованный шаблон
- `params` - параметры подстановки (JSON)
- `recipients` - список получателей (JSON)
- `status` - статус отправки (prepared/sent/error)
- `error_text` - текст ошибки при неудаче

## Типы уведомлений

### Email уведомления
Поддерживаемые возможности:
- **HTML письма** с CSS стилями
- **Jinja2 шаблонизация** для динамического контента
- **Встроенные изображения** через Content-ID
- **Множественные получатели**
- **Настраиваемая тема** письма

### Планируемые типы
- **SMS уведомления** через внешние провайдеры
- **Push уведомления** для мобильных приложений
- **Telegram боты** для уведомлений

## Система шаблонов

### Шаблон подтверждения email
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <title>Подтверждение электронной почты</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto;">
        <img src="cid:logo" alt="Domain.com" style="width:150px;" />
        <h1>Подтверждение электронной почты</h1>
        <p>Здравствуйте!</p>
        <p>Для подтверждения регистрации перейдите по ссылке:</p>
        <a href="{{url}}">Подтвердить email</a>
    </div>
</body>
</html>
```

### Переменные шаблона
Поддерживаются Jinja2 переменные:
- `{{url}}` - ссылка для подтверждения

### Встроенные изображения
```html
<img src="cid:logo" alt="Логотип" />
```
Где `logo` - это CID вложения из AttachmentModel.

## Сервис уведомлений

### NotificationService
Основной сервис для отправки уведомлений:

```python
class NotificationService:
    async def notify(self, notification_data: dict)
    async def send_email(self, recipient_data)
    async def get_template_by_code(self, code: str) -> TemplateModel
    async def write_log(self, status: str, columns: dict = None)
```

### Процесс отправки email

1. **Получение шаблона** по коду
2. **Рендеринг HTML** с подстановкой переменных
3. **Подготовка вложений** из base64 в временные файлы
4. **Создание лога** со статусом "prepared"
5. **Отправка через SMTP**
6. **Обновление лога** (success/error)
7. **Очистка временных файлов**

## API использования

### Отправка уведомления
```python
notification_data = {
    "type": "email",
    "code": "confirm_email", 
    "recipients": [
        {
            "emails": ["user@example.com"],
            "params": {
                "url": "https://app.com/confirm?token=abc123"
            }
        }
    ]
}

await notification_service.notify(notification_data)
```

### Через BackgroundTasks
```python
@router.post("/register/")
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks
):
    user = await create_user(user_data)
    
    # Отправка в фоне
    background_tasks.add_task(
        notification_service.notify,
        {
            "type": "email",
            "code": "confirm_email",
            "recipients": [{
                "emails": [user.email],
                "params": {"url": f"https://app.com/confirm?token={user.token}"}
            }]
        }
    )
    
    return user
```

## Схемы данных

### RecipientsSchema
Схема для запроса отправки:
```python
class RecipientsSchema(BaseSchema):
    type: NotificationTypeEnum = NotificationTypeEnum.email
    code: str                               # Код шаблона
    recipients: list[EmailRecipient | SMSRecipient]
```

### EmailRecipient
Получатель email уведомления:
```python
class EmailRecipient(BaseRecipient):
    emails: list[EmailStr]                  # Список email адресов
    params: dict                            # Параметры для шаблона
```

### NotificationTypeEnum
Типы уведомлений:
```python
class NotificationTypeEnum(StrEnum):
    sms: str = "sms", "СМС"
    email: str = "email", "Электронная почта"  
    push: str = "push", "Push уведомление"
```

### NotificationLogStatusEnum
Статусы отправки:
```python
class NotificationLogStatusEnum(StrEnum):
    prepared: str = "prepared", "Подготовлено"
    sent: str = "sent", "Отправлено"
    error: str = "error", "Ошибка отправки"
```

## SMTP конфигурация

### Настройки подключения
```python
# Локальная разработка с Gmail
if config.environment == ApiMode.local and "gmail" in config.smtp.server:
    smtp_client = FastMail(ConnectionConfig(
        MAIL_SERVER=config.smtp.server,
        MAIL_PORT=config.smtp.port, 
        MAIL_USERNAME=config.smtp.username,
        MAIL_PASSWORD=config.smtp.password,
        MAIL_FROM_NAME=config.smtp.from_name,
        MAIL_FROM=config.smtp.from_email,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=False,
    ))
```

### Переменные окружения
```bash
# SMTP настройки
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM_NAME="Windi Messenger"
MAIL_FROM_EMAIL=noreply@windi.com
MAIL_TIMEOUT=10
```

## Встроенные шаблоны

### Подтверждение email (confirm_email)
- **Тема**: "Подтверждение эл. почты"
- **Переменные**: `{{url}}` - ссылка подтверждения
- **Вложения**: логотип компании
- **Использование**: при регистрации пользователей

### Сброс пароля (reset_password)  
- **Тема**: "Запрос на изменение пароля"
- **Переменные**: `{{url}}` - ссылка для сброса
- **Вложения**: логотип компании
- **Использование**: при восстановлении пароля

## Работа с вложениями

### Подготовка вложений
```python
def _prepare_attachments(self, attachments: list[AttachmentModel]):
    temp_files = []
    prepared = []
    
    for attachment in attachments:
        # Декодирование base64 в временный файл
        temp_path = self._save_base64_to_temp_file(
            attachment.base64, 
            attachment.filename
        )
        temp_files.append(temp_path)
        
        # Настройка для FastMail
        prepared.append({
            "file": temp_path,
            "headers": {
                "Content-ID": f"<{attachment.cid}>",
                "Content-Disposition": f'inline; filename="{attachment.filename}"'
            },
            "mime_type": "image",
            "mime_subtype": "svg",
        })
    
    return temp_files, prepared
```

### Очистка временных файлов
```python
def _cleanup_temp_files(self, paths: list[str]):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
```

## Логирование и мониторинг

### Создание лога отправки
```python
await self.write_log(
    status=NotifyStatus.prepared,
    columns={
        "template_id": template.id,
        "params": recipient.params,
        "recipients": {"emails": recipient.emails},
    }
)
```

### Обновление статуса
```python
# При успешной отправке
await self.write_log(status=NotifyStatus.sent, log_id=log_id)

# При ошибке
await self.write_log(
    status=NotifyStatus.error,
    columns={"error_text": str(err)}, 
    log_id=log_id
)
```

### SQL запросы для мониторинга
```sql
-- Статистика отправок за день
SELECT status, COUNT(*) 
FROM notification_log 
WHERE created_at >= NOW() - INTERVAL '1 day'
GROUP BY status;

-- Самые частые ошибки
SELECT error_text, COUNT(*)
FROM notification_log  
WHERE status = 'error'
GROUP BY error_text
ORDER BY COUNT(*) DESC;

-- Популярные шаблоны
SELECT t.code, t.subject, COUNT(nl.id) as sends
FROM notification_template t
LEFT JOIN notification_log nl ON t.id = nl.template_id
GROUP BY t.id, t.code, t.subject
ORDER BY sends DESC;
```

## Обработка ошибок

### Типы ошибок
```python
class BaseNotificationException(BaseAppException):
    status_code = 500
    code = ErrorCode.notify_error
    detail = "Notification Exception"

class NotificationTypeNotAllowed(BaseNotificationException):
    status_code = 405  
    detail = "Notification type not allowed"
```

### Логирование ошибок
- **WARNING** - ошибки отправки email
- **INFO** - успешные отправки
- **ERROR** - системные ошибки сервиса

## Тестовые данные

### Фабрика шаблонов
```python
notification_templates = {
    "target_class": "app.modules.notify_module.db.models:TemplateModel",
    "data": [
        {
            "id": uuid4(),
            "type": "email",
            "code": "confirm_email", 
            "subject": "Подтверждение эл. почты",
            "body": "<!DOCTYPE html>..."
        }
    ]
}
```

### Фабрика вложений
```python
notification_attachments = {
    "target_class": "app.modules.notify_module.db.models:AttachmentModel", 
    "data": [
        {
            "id": uuid4(),
            "filename": "logo.svg",
            "cid": "logo",
            "base64": "PHN2ZyB3aWR0aD0iMjAwIi...",
            "!refs": {
                "template_id": {
                    "target_class": "app.modules.notify_module.db.models:TemplateModel",
                    "criteria": {"code": "confirm_email"},
                    "field": "id"
                }
            }
        }
    ]
}
```

## Интеграция с другими модулями

### Auth Module
- **Подтверждение email** при регистрации
- **Сброс пароля** через email
- **Уведомления о входе** с нового устройства

### Chat Module (планируется)
- **Уведомления о сообщениях** при оффлайне
- **Дайджесты активности** в чатах
- **Приглашения в групповые чаты**

## Производительность

### Оптимизации
- **Фоновая отправка** через BackgroundTasks
- **Переиспользование подключений** SMTP
- **Кэширование шаблонов** в памяти
- **Пакетная отправка** нескольким получателям

### Ограничения
- **Размер вложений**: до 25MB на письмо
- **Количество получателей**: до 50 в одном письме
- **Rate limiting**: зависит от SMTP провайдера

## Примеры использования

### Создание нового шаблона
```python
# 1. Добавить в базу данных
template = TemplateModel(
    type="email",
    code="welcome_email",
    subject="Добро пожаловать!",
    body="""
    <h1>Добро пожаловать, {{username}}!</h1>
    <p>Спасибо за регистрацию в нашем сервисе.</p>
    <img src="cid:welcome_image" alt="Добро пожаловать" />
    """
)

# 2. Добавить вложение
attachment = AttachmentModel(
    template_id=template.id,
    filename="welcome.jpg", 
    cid="welcome_image",
    base64="iVBORw0KGgoAAAANSUhEUgAA..."
)

# 3. Использовать в коде
await notification_service.notify({
    "type": "email",
    "code": "welcome_email",
    "recipients": [{
        "emails": ["user@example.com"],
        "params": {"username": "Иван"}
    }]
})
```

### Отправка с множественными получателями
```python
await notification_service.notify({
    "type": "email", 
    "code": "newsletter",
    "recipients": [{
        "emails": [
            "user1@example.com",
            "user2@example.com", 
            "user3@example.com"
        ],
        "params": {
            "newsletter_title": "Новости недели",
            "unsubscribe_url": "https://app.com/unsubscribe"
        }
    }]
})
```

### Обработка ошибок отправки
```python
try:
    await notification_service.notify(data)
except NotificationTypeNotAllowed:
    logger.error("Unsupported notification type")
except Exception as e:
    logger.error(f"Failed to send notification: {e}")
    # Можно добавить в очередь для повторной отправки
```

## 🔮 Планы развития

### Краткосрочные планы
- **SMS уведомления** через Twilio/SMS.ru
- **Push уведомления** для мобильных приложений
- **Webhook уведомления** для интеграций
- **Очередь повторных отправок** при ошибках

### Долгосрочные планы
- **A/B тестирование** шаблонов
- **Персонализация контента** на основе данных пользователя
- **Аналитика открытий** и кликов в письмах
- **Автоматические триггеры** на события в системе
- **Визуальный редактор** шаблонов
- **Мультиязычность** шаблонов

### Интеграции
- **Telegram боты** для уведомлений
- **Slack интеграция** для команд
- **Discord webhook** для сообществ
- **External API** для сторонних сервисов

## Безопасность

### Защита данных
- **Валидация email адресов** через Pydantic
- **Санитизация HTML** в шаблонах
- **Ограничение размера** вложений
- **Rate limiting** отправок

### Приватность
- **Логирование без персональных данных**
- **Автоматическое удаление** старых логов
- **Обфускация email** в логах
- **GDPR совместимость** для удаления данных
