# Celery Health Checker (celery_hchecker)

Набор утилит для проверки работоспособности Celery: брокера, backend-а результатов и воркеров.
Простая, расширяемая и тестируемая библиотека с поддержкой кеширования результатов (память / Redis) и фонового мониторинга.

## Особенности
- Проверяет три аспекта Celery:
  - `broker` — соединение с брокером (kombu.Connection);
  - `backend` — запись/чтение результата в/result backend (store_result / get_task_meta);
  - `workers` — состояние зарегистрированных воркеров (inspect.ping(), inspect.active()).
- Встроенная поддержка кеша:
  - `MemoryCache` (TTLCache);
  - `RedisCache` (совместим с redis-py).
- Фоновый мониторинг (daemon thread) с настраиваемым интервалом.
- Мокабельная архитектура — легко юнит-тестировать.

## Установка

```bash
# в виртуальном окружении
pip install celery          # если ещё не установлен
pip install cachetools      # MemoryCache использует cachetools.TTLCache
pip install redis           # Если вы собираетесь использовать redis для кеширования результата

# Установите ваш пакет локально (разработка)
pip install -e .
```

Dev-зависимости (рекомендуется для тестирования):
```bash
pip install pytest fakeredis testcontainers pytest-mock
```

## Быстрый старт
### 1. Создайте Celery app (пример proj/celery_app.py):
```python
from celery import Celery

app = Celery("proj", broker="redis://127.0.0.1:6379/0", backend="redis://127.0.0.1:6379/1")

@app.task
def add(x, y):
    return x + y
```
### 2. Подключите `CeleryHealthChecker`:
```python
from celery_hchecker.healthcheker import CeleryHealthChecker
from celery_hchecker.cache.memory import MemoryCache

ch = CeleryHealthChecker(app=app, cache=MemoryCache(ttl=10), interval=10)
print(ch.force_check())      # выполнило все проверки
print(ch.is_healthy)         # быстрое чтение из кеша (если есть)
print(ch.get_stats())        # статистика
```
### 3. Запустить фоновой мониторинг:
```python
ch.start()
# ... в конце:
ch.stop()
```

## API / основные компоненты
### `ICache` (interface)

Методы:
- `get(key: str) -> Optional[Tuple[bool, float, Optional[str]]]`
- `set(key: str, value: bool, latency: float, error: Optional[str]) -> None`

### `MemoryCache`
Параметры конструктора:
- `maxsize: int = 1000, ttl: int = 60`

### `RedisCache`
Параметры конструктора:
- `client — клиент совместимый с redis-py (StrictRedis/Redis)`
- `ttl: int = 60, prefix: str = "celery_health_"`

### Checkers
- `BrokerChecker(broker_url: str, timeout: int=3, retries: int=3, delay: float=0.5)`
- `BackendChecker(backend: BaseBackend, cleanup: bool = True, timeout: float=5.0, wait: float=1.0)`
- `WorkersChecker(app: Celery, timeout: float=5.0, retries: int=3, delay: float=0.5)`

Все чекеры реализуют:
- `name() -> str`
- `check() -> Tuple[bool, float, Optional[str]] — (ok, latency_seconds, error_or_None)`

### `CeleryHealthChecker`
Конструктор:
```python
CeleryHealthChecker(
    *,
    app,
    cache: Optional[ICache] = None,
    interval: int = 30,
    enable_cleanup: bool = True,
    backend_poll_wait: float = 1.0,
)
```

Методы:
- `start(), stop(join_timeout: float = None)`
- `force_check() -> bool` — запускает все проверки синхронно, кэширует per-checker и aggregate health
- `get_stats() -> dict`
- `is_healthy -> bool` (свойство) — пытается прочитать агрегатный health из кэша, иначе вызывает force_check()
- `get_instance()` — возвращает singleton-экземпляр (в текущей реализации класс устроен как singleton через __new__)

## Примеры использования
### Пример: встроенный мониторинг (daemon thread)
```python
from time import sleep
from celery_hchecker.cache.memory import MemoryCache
from celery_hchecker.healthcheker import CeleryHealthChecker

checker = CeleryHealthChecker(app=app, cache=MemoryCache(ttl=10), interval=10)
checker.start()

try:
    while True:
        print("Healthy:", checker.is_healthy)
        print("Stats:", checker.get_stats())
        sleep(10)
except KeyboardInterrupt:
    checker.stop()
```

### Пример: HTTP endpoint (FastAPI)
```python
from fastapi import FastAPI
from celery_hchecker.cache.redis import RedisCache
import redis

rclient = redis.Redis(host="127.0.0.1", port=6379, db=2)
cache = RedisCache(client=rclient, ttl=10)

checker = CeleryHealthChecker(app=app, cache=cache, interval=15)

api = FastAPI()

@api.get("/health")
def health():
    return {
        "healthy": checker.is_healthy,
        "stats": checker.get_stats()
    }
```

## Кэширование
- Пер-чекер ключи: `health:{checker_name}` (например `health:broker`, `health:backend`, `health:workers`).
Значение: `(ok: bool, latency: float, error: Optional[str])`.
- Агрегированный ключ: `health` — хранит итоговую булевую метрику (и latency aggregate в payload).

## Логирование
Компонент использует стандартный logging с логгером CeleryHealthChecker.
Уровень логирования можно настроить:

```python
import logging
logging.getLogger('CeleryHealthChecker').setLevel(logging.DEBUG)
```

## Ограничения
- Поддерживаются только брокеры/бэкенды, совместимые с Kombu
- Для проверки воркеров требуется доступ к Celery Control API

## Лицензия
MIT License