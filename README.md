# Messenger Backend

## Запуск и установка:

### localhost
1. Для первого запуска надо настроить переменные окружения
2. Установить зависимости из `requirements.txt`
3. Запустить основной исполняемый файл `./main.py`:
    1. `python3 main.py`
    2. http://localhost:8788/

### docker-compose
1. Установить переменные окружения
2. `docker compose up`


### Подключение нового модуля:
Чтобы реализовать новый модуль, необходимо запустить python скрипт:
```bash
python create_module.py
Введите латинское название модуля:
-> some_module

-> Модуль some_module успешно создан!
```
После этого будет создана необходимая структура файлов и папок. 
После запуска прожекта, автоимпорт автоматом подтянет ендпоинты из нового модуля, если они были созданы.

### Переменные окружения:
- API settings
  - `API_TITLE`: заголовок свагера. Пример: "Messenger REST-API engine"
  - `API_SERVICE_PORT`: Сервисный порт
  - `API_CONTACT_NAME`: Контактное лицо разработчика.
  - `API_CONTACT_EMAIL`Контактная почта разработчика.
  - `API_MODE`: Режим поведения апишки: PROD, DEV, LOCAL
  - `ENVIRONMENT` Окружение приложения, от него может зависеть некоторое поведение: PROD, DEV, LOCAL
  - `API_VERSION`: Версия продукта
  - `API_RELOAD`: Автоматическая перезагрузка, по умолчанию `true`
  - `APPLICATION_ENABLED_MODULES`: Подключаемые модули. По умолчанию: `BASE`

- Database settings
  - `PG_SERVER_ADDRESS`: адрес
  - `PG_SERVER_PORT`: порт
  - `PG_SERVER_LOGIN`: логин
  - `PG_SERVER_PASSWD`: пароль
  - `PG_SERVER_DB`: имя базы данных

- Logging settings
  - `LOG_ENABLE`: Вкл/выкл основной логер. По умолчанию `True`
  - `LOG_LEVEL`: Уровень логирования системы. По умолчанию `INFO`
  - `LOG_WRITE_TO_FILE`: Переключатель для записи логов файл. По умолчанию `True`

> Тут описаны только базовые настройки, остальные можно рассмотреть в модуле `app/core/settings`

## Схема БД
![БД](./db_schema.png)

## Notes:
Расширение используемое в БД
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SELECT uuid_generate_v4();
```
Оно используется в наследуемой модели для автоматической установки id таблицы

## Структура проекта
```
.
├── Dockerfile
├── README.md
├── alembic.ini
├── app
│   ├── adapters                        - адаптеры для внешних запросов
│   │   ├── base                        - базовые клиенты
│   │   ├── clients                     - клиенты для подключения к внешним источникам
│   │   ├── db                          - адаптер Базы Данных
│   │   │   └── migrations              - миграции базы данных
│   │   └── errors.py
│   ├── dependencies                    - dependency injection для FastAPI
│   │   ├── dependency_db.py            - получение сессии
│   │   └── services_dependency.py      - получение сервисов
│   ├── fastapi_engine
│   │   ├── app.py
│   │   ├── constructor.py
│   │   ├── events                      - события, для приложения
│   │   │   └── startup.py              - инициализация событий при старте приложения
│   │   └── middlewares                 - мидлвари для фастапи
│   │       ├── cors_middleware.py      - мидлварь CORS
│   │       ├── errors_middleware.py    - обработчик Exception, который не предусмотрели в базовой логике
│   │       └── log_middleware.py       - логирование запроса/ответа
│   ├── modules
│   │   ├── base_module                 - базовый модуль, в нем хранятся наследуемые объекты
│   │   ├── catalogues_module           - модуль справочников
│   │   └── healthcheck_module          - healthcheck module
│   ├── resources                       - хранение констант
│   │   └── constants.py
│   ├── services                        - базовые сервисные ошибки
│   │   └── errors.py
│   ├── settings                        - базовые настройки приложения
│   │   ├── base.py                     - базовые настройки
│   │   ├── app_settings.py             - настрофки FastAPI
│   │   ├── db_settings.py              - настройки БД
│   │   ├── log.py                      - настройки логов
│   │   └── modules_settings.py         - настройки подключаемых модулей
│   └── utils
│       ├── err_message.py              - текст ошибки, который присылается при обработке Exception в АПИ
│       ├── module_creator              - создание новых модулей
│       │   ├── base_creator.py         - базовый функционал
│       │   ├── creator.py              - основной исполняемый класс
│       │   └── __init__.py             - содержит функцию для создания модулей
│       └── setup_modules.py            - установка модулей определяемых переменными окружения
├── manage.py                           - многофункциональный скрипт
├── docker-compose.yml
├── logs                                - папка для хранения логов приложения
├── main.py                             - основной запускаемый файл
├── pyproject.toml                      - настройки проекта
├── requirements-dev.txt                - зависимости проекта включая пакеты для тестирования
├── requirements.txt                    - зависимости проекта
└── tests                               - базовый тестовый модуль
    ├── conftest.py                     - импорт фикстур для использования pytest
    ├── fakers.py                       - фейковые клиенты, имитирующие поведение клиентов
    └── fixtures.py                     - базоыве фикстуры

```
