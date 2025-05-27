# Healthcheck Module
Модуль проверки состояния системы и внешних зависимостей для мониторинга и обеспечения надежности приложения.

## Назначение модуля
Healthcheck Module решает задачи мониторинга системы:

- **Проверка состояния базы данных** и подключений
- **Мониторинг внешних сервисов** и API
- **Быстрая диагностика** проблем в продакшене
- **Интеграция с системами мониторинга** (Prometheus, Grafana)
- **Load balancer health checks** для Kubernetes/Docker
- **Автоматическое восстановление** при сбоях

## Структура модуля

```
healthcheck_module/
├── api/
│   └── routes/
│       └── healthcheck.py       # Эндпоинт проверки здоровья
├── db/
│   ├── cruds/
│   │   └── health_crud.py       # CRUD для проверок БД
│   └── models/                  # Модели (пусто - используется Base)
├── schemas/                     # Схемы (пусто - простые ответы)
├── services/
│   └── health_service.py        # Бизнес-логика проверок
├── tests/
│   ├── conftest.py              # Настройка тестов
│   ├── test_api.py              # Тесты API
│   └── test_service.py          # Тесты сервиса
└── README.md                    # Документация модуля
```

## API Эндпоинты

### GET /healthcheck/
Основной эндпоинт проверки состояния системы.

#### Успешный ответ (200 OK)
```json
{
  "status": "success",
  "data": {
    "health": "ok"
  }
}
```

#### Ошибка базы данных (500 Internal Server Error)
```json
{
  "status": "error", 
  "error": "database \"database_not_exist\" does not exist"
}
```

## Компоненты модуля

### HealthService
Основной сервис для проверки состояния:
```python
class HealthService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self.crud = HealthCRUD(self.session)

    async def check_health(self):
        answer = await self.crud.check_connect()
        logging.debug("DB ok")
        return {"health": "ok"}
```

### HealthCRUD
CRUD для проверки подключения к базе данных:
```python
class HealthCRUD:
    def __init__(self, session):
        self.session = session

    async def check_connect(self):
        q = text("SELECT 1")  # Простой запрос для проверки
        res = await self.session.execute(q)
        return res.scalar()
```

### API Handler
Обработчик эндпоинта с обработкой ошибок:
```python
@router.get("/", name="healthcheck:get")
async def check_health(
    service: HealthService = Depends(get_service(HealthService)),
):
    try:
        return await service.check_health()
    except Exception as err:
        logging.exception(f"ERROR: {err}")
        return err_msg(
            status_code=500,
            error_body={"status": "error", "error": f"{err}"},
        )
```

## Типы проверок
### Базовые проверки
1. **База данных** - выполнение простого SELECT запроса
2. **Подключения** - проверка pool соединений
3. **Время отклика** - измерение latency

### Расширенные проверки (планируется)
1. **Внешние API** - проверка доступности сторонних сервисов
2. **Redis/Cache** - состояние кэширования
3. **Файловая система** - доступность дискового пространства
4. **Memory usage** - использование оперативной памяти
5. **CPU load** - нагрузка на процессор

## Форматы ответов
### Детальный healthcheck (планируется)
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T12:00:00Z", 
  "version": "0.1.a",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45,
      "details": "PostgreSQL connection OK"
    },
    "redis": {
      "status": "healthy", 
      "response_time_ms": 12,
      "details": "Redis ping successful"
    },
    "external_api": {
      "status": "degraded",
      "response_time_ms": 2500,
      "details": "Slow response from payment gateway"
    }
  },
  "dependencies": {
    "database": "required",
    "redis": "optional", 
    "external_api": "optional"
  }
}
```

## Мониторинг и интеграции

### Kubernetes Liveness Probe
```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: messenger-api
    image: messenger-api:latest
    livenessProbe:
      httpGet:
        path: /healthcheck/
        port: 8788
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
```

### Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8788/healthcheck/ || exit 1
```

### Load Balancer Configuration
```nginx
upstream messenger_backend {
    server messenger-api-1:8788;
    server messenger-api-2:8788;
    
    # Health check configuration
    health_check uri=/healthcheck/ interval=10s;
}
```

### Prometheus Metrics (планируется)
```
# HELP messenger_health_check_duration_seconds Time spent on health checks
# TYPE messenger_health_check_duration_seconds histogram
messenger_health_check_duration_seconds_bucket{check="database",le="0.1"} 245
messenger_health_check_duration_seconds_bucket{check="database",le="0.5"} 312

# HELP messenger_health_check_status Health check status (1=healthy, 0=unhealthy)
# TYPE messenger_health_check_status gauge
messenger_health_check_status{check="database"} 1
messenger_health_check_status{check="redis"} 0
```

## Тестирование

### Unit тесты сервиса
```python
class TestHealthService:
    async def test_health_ok(self, health_service):
        result = await health_service.check_health()
        assert result == {"health": "ok"}

    async def test_health_raises_db_error(self, incorrect_health_service):
        with pytest.raises(OperationalError) as err:
            await incorrect_health_service.check_health()
        assert 'database "database_not_exist" does not exist' in str(err.value)
```

### Integration тесты API
```python
class TestHealthcheckAPI:
    async def test_health_api_200(self, app, client):
        response = await client.get(app.url_path_for("healthcheck:get"))
        assert response.status_code == 200

    async def test_health_api_500(self, incorrect_app, client):
        response = await client.get(incorrect_app.url_path_for("healthcheck:get"))
        resp_json = response.json()
        assert response.status_code == 500
        assert 'database "database_not_exist" does not exist' in resp_json["error"]
```

### Фикстуры для тестов
```python
@pytest.fixture(scope="function")
async def incorrect_health_service(session_not_exists):
    return HealthService(session_not_exists)

def incorrect_connect():
    test_db_settings = DBSettings()
    test_db_settings.db = "database_not_exist"
    # Создание некорректного подключения для тестов
    return async_session_maker
```


## Конфигурация

### Переменные окружения
```bash
# Health check настройки (планируется)
HEALTH_CHECK_TIMEOUT=30                   # Таймаут проверок в секундах
HEALTH_CHECK_EXTERNAL_APIS=true           # Проверять внешние API
HEALTH_CHECK_REDIS=false                  # Проверять Redis (если есть)
HEALTH_CHECK_DETAILED=false               # Детальные проверки
```

### Настройка уровней проверок
```python
class HealthLevel(Enum):
    BASIC = "basic"           # Только БД
    STANDARD = "standard"     # БД + основные сервисы  
    COMPREHENSIVE = "comprehensive"  # Все зависимости
```

## Обработка ошибок

### Типы ошибок
1. **Database errors** - проблемы с подключением к БД
2. **Timeout errors** - превышение времени ожидания
3. **Connection errors** - сетевые проблемы
4. **Service unavailable** - недоступность зависимостей

### Graceful degradation
```python
async def check_health_with_fallback(self):
    try:
        # Основная проверка
        return await self.full_health_check()
    except DatabaseError:
        # Fallback на упрощенную проверку
        return {"health": "degraded", "reason": "database_issues"}
    except Exception:
        # Минимальная проверка
        return {"health": "unknown", "reason": "check_failed"}
```

## Жизненный цикл проверок

### 1. Startup Health Check
```python
async def startup_health_check():
    """Проверка при запуске приложения"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await health_service.check_health()
            logger.info("Startup health check passed")
            return
        except Exception as e:
            logger.warning(f"Startup health check failed (attempt {attempt + 1}): {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    raise RuntimeError("Application failed startup health checks")
```

### 2. Runtime Health Checks
```python
async def periodic_health_check():
    """Периодические проверки во время работы"""
    while True:
        try:
            result = await health_service.check_health()
            metrics.record_health_check_success()
        except Exception as e:
            metrics.record_health_check_failure()
            logger.error(f"Health check failed: {e}")
        
        await asyncio.sleep(60)  # Проверка каждую минуту
```

### 3. Shutdown Health Check
```python
async def shutdown_health_check():
    """Проверка при завершении работы"""
    try:
        # Graceful shutdown компонентов
        await cleanup_resources()
        logger.info("Shutdown completed successfully")
    except Exception as e:
        logger.error(f"Shutdown health check failed: {e}")
```

## Использование в production

### Мониторинг дашборд
```grafana
# Grafana dashboard панели
- Health Check Success Rate (last 24h)
- Average Response Time (last 1h) 
- Failed Health Checks (last 6h)
- Dependency Status Matrix
- Alert History
```

### Автоматическое восстановление
```bash
#!/bin/bash
# Health check скрипт для systemd/supervisord

check_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8788/healthcheck/)
    if [ $response -eq 200 ]; then
        echo "Health check passed"
        return 0
    else
        echo "Health check failed with code $response"
        return 1
    fi
}

# Перезапуск при неудаче
if ! check_health; then
    echo "Restarting messenger service..."
    systemctl restart messenger-api
fi
```

## Планы развития

### Краткосрочные планы
- **Детальные проверки** состояния компонентов
- **Проверка внешних API** и сервисов
- **Кастомные health checks** для бизнес-логики

### Долгосрочные планы
- **Distributed health checks** для microservices
- **Health check orchestration** с зависимостями
- **Auto-healing capabilities** при обнаружении проблем


## Безопасность
### Защита эндпоинта
```python
# Опциональная авторизация для детальных проверок
@router.get("/detailed")
async def detailed_health_check(
    account: Annotated[get_account_from_token, Depends()],
    service: HealthService = Depends(get_service(HealthService))
):
    # Только для авторизованных пользователей
    return await service.detailed_health_check()
```

## Best Practices

### 1. Быстрые проверки
- Health check должен выполняться быстро (< 1 секунды)
- Избегать тяжелых операций в basic проверках
- Использовать connection pooling

### 2. Информативные ошибки
- Четкие сообщения об ошибках
- Не раскрывать чувствительную информацию
- Логирование для диагностики

### 3. Устойчивость
- Таймауты для всех проверок
- Graceful degradation при частичных сбоях
- Retry logic с exponential backoff

### 4. Мониторинг
- Метрики для всех типов проверок
- Алерты на критические компоненты
- Дашборды для визуализации состояния
