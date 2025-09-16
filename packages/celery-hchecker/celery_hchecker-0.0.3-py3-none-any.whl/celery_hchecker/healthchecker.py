import logging
import threading
import time
import typing as tp

from .cache.base import ICache
from .cache.memory import MemoryCache
from .checkers import BackendChecker, BrokerChecker, WorkersChecker


class CeleryHealthChecker:
    """
        Монитор состояния Celery (broker, backend, workers).

        Особенности:
        - Безопасен для многопоточного доступа (использует RLock).
        - Кэширует результаты отдельно для каждого чекера (ключ: health:{name})
          и агрегированный результат под ключом 'health'.
        - Опционально можно зарегистрировать global instance через set_global_instance.
        """

    # Global instance management
    _instance_lock = threading.Lock()
    _instance: tp.Optional["CeleryHealthChecker"] = None

    @classmethod
    def get_instance(cls) -> tp.Optional["CeleryHealthChecker"]:
        if cls._instance is None:
            raise RuntimeError("CeleryHealthChecker has not been initialized.")

        with cls._instance_lock:
            return cls._instance

    @property
    def is_initialized(self) -> bool:
        """Признак того, что объект создан (всегда True после __init__)."""
        return self._instance is not None

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(
            self,
            *,
            app,
            cache: tp.Optional["ICache"] = None,
            interval: int = 30,
            enable_cleanup: bool = True,
            backend_poll_wait: float = 1.0,
    ):
        """
        :param app: Celery app
        :param cache: реализация ICache (если None — используется MemoryCache с TTL=interval)
        :param interval: интервал мониторинга (сек)
        :param enable_cleanup: если True — BackendChecker будет пытаться очищать метаданные
        :param backend_poll_wait: время (в сек) ожидания результата backend при проверке
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._app = app
        self._interval = int(interval)
        self._enable_cleanup = bool(enable_cleanup)
        self._backend_poll_wait = float(backend_poll_wait)

        # Кэш: если не передан, используем MemoryCache с TTL = interval
        if cache is None:
            try:
                # предполагается, что MemoryCache определён рядом
                self._cache = MemoryCache(ttl=self._interval)
            except Exception as exc:
                # в крайнем случае — простой dict-каше (не TTL)
                self._cache = None  # будем обрабатывать при использовании
                self._logger.warning("MemoryCache not available; cache disabled", exc_info=exc)
        else:
            self._cache = cache

        # Потоковые примитивы
        self._stop = threading.Event()
        self._lock = threading.RLock()
        self._thread: tp.Optional[threading.Thread] = None

        # Статистика
        self._stats = {
            "total": 0,
            "success": 0,
            "last_errors": {},  # checker_name -> error_text
        }

        # Init checkers list
        self._checkers: tp.List[tp.Any] = []
        try:
            broker_url = getattr(self._app.conf, "broker_url", None)
        except Exception:
            broker_url = None
        try:
            result_backend = getattr(self._app.conf, "result_backend", None)
        except Exception:
            result_backend = None

        if broker_url:
            try:
                self._checkers.append(BrokerChecker(broker_url))
            except Exception as exc:
                self._logger.warning("Failed to init BrokerChecker", exc_info=exc)

        if result_backend:
            try:
                # Передать параметр cleanup в BackendChecker
                self._checkers.append(BackendChecker(self._app.backend, cleanup=self._enable_cleanup, timeout=5.0,
                                                     wait=self._backend_poll_wait))
            except Exception as exc:
                self._logger.warning("Failed to init BackendChecker", exc_info=exc)

        # WorkersChecker — всегда добавляем, т.к. проверяет состояние воркеров
        try:
            self._checkers.append(WorkersChecker(self._app))
        except Exception as exc:
            self._logger.warning("Failed to init WorkersChecker", exc_info=exc)

    # ----- Мониторинг -----
    def _monitor(self) -> None:
        """Фоновый цикл, который периодически вызывает force_check()."""
        self._logger.debug("Monitor thread started")
        while not self._stop.wait(timeout=self._interval):
            try:
                self.force_check()
            except Exception:
                # Защищаем поток от падения: логируем ошибку, продолжаем
                self._logger.exception("Unhandled exception in monitor loop")

        self._logger.debug("Monitor thread stopped")

    def start(self) -> None:
        """Запустить фоновый мониторинг (daemon thread)."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._logger.warning("Monitoring already running")
                return
            self._stop.clear()
            self._thread = threading.Thread(target=self._monitor, name="CeleryHealthMonitor", daemon=True)
            self._thread.start()
            self._logger.info("Started health monitoring")

    def stop(self, join_timeout: float = None) -> None:
        """
        Остановить фоновой мониторинг.
        :param join_timeout: время для join(); по умолчанию 1.5 * interval
        """
        with self._lock:
            self._stop.set()
            if self._thread:
                timeout = join_timeout if join_timeout is not None else (self._interval * 1.5)
                self._thread.join(timeout=timeout)
                if self._thread.is_alive():
                    self._logger.warning("Monitor thread did not stop within timeout")
                else:
                    self._logger.info("Monitor thread stopped")
                self._thread = None

    # ----- Статистика -----
    def get_stats(self) -> dict:
        """Возвращает копию статистики и вычисляет success_rate."""
        with self._lock:
            total = int(self._stats.get("total", 0))
            success = int(self._stats.get("success", 0))
            rate = (success / total) if total else 0.0
            # Возвращаем копию, чтобы внешний код не мутировал внутреннее состояние
            return {
                "total": total,
                "success": success,
                "last_errors": dict(self._stats.get("last_errors", {})),
                "success_rate": rate,
            }

    # ----- Основная проверка -----
    def force_check(self) -> bool:
        """
        Выполняет все проверки синхронно, записывает per-checker результаты в кэш и
        агрегированный результат под ключом 'health'.
        Возвращает True, если все проверки успешны.
        """
        overall = True
        results: tp.Dict[str, bool] = {}
        details: tp.Dict[str, dict] = {}

        start_all = time.monotonic()
        for chk in list(self._checkers):
            try:
                name = chk.name()
            except Exception:
                name = getattr(chk, "__class__", type(chk)).__name__

            try:
                ok, latency, err = chk.check()
            except Exception as exc:
                # Защитный catch — если checker упал, отмечаем как failed
                self._logger.exception("Checker %s raised an exception", name)
                ok, latency, err = False, 0.0, f"exception: {exc}"

            results[name] = bool(ok)
            details[name] = {"ok": bool(ok), "latency": float(latency), "error": err}

            # Кэш per-checker
            cache_key = f"health:{name}"
            try:
                if self._cache is not None:
                    # ICache.set signature: set(key, value: bool, latency: float, error: Optional[str])
                    self._cache.set(cache_key, bool(ok), float(latency), err)
            except Exception as exc:
                self._logger.warning("Failed to set cache for %s", cache_key, exc_info=exc)

            if not ok:
                overall = False

        total_latency = time.monotonic() - start_all
        # Сохраняем агрегированный результат
        aggregate_error = None
        if not overall:
            aggregate_error = {k: details[k]["error"] for k in details if not details[k]["ok"]}

        try:
            if self._cache is not None:
                # latency for aggregate: use total_latency
                self._cache.set("health", bool(overall), float(total_latency),
                               str(aggregate_error) if aggregate_error else None)
        except Exception as exc:
            self._logger.warning("Failed to set aggregate health cache", exc_info=exc)

        # Обновляем stats
        with self._lock:
            self._stats["total"] = int(self._stats.get("total", 0)) + 1
            if overall:
                self._stats["success"] = int(self._stats.get("success", 0)) + 1
            self._stats["last_errors"] = {k: details[k]["error"] for k in details if not details[k]["ok"]}

            return bool(overall)

    # ----- Быстрый доступ к здоровью -----
    @property
    def is_healthy(self) -> bool:
        """
        Быстрая проверка статуса: пытается получить агрегированный health из cache,
        если его нет — делает force_check().
        """
        try:
            if self._cache is not None:
                cached = self._cache.get("health")
                if cached:
                    # cached expected: (value: bool, latency: float, error: Optional[str])
                    return bool(cached[0])
        except Exception as exc:
            self._logger.warning("Cache read failed when checking is_healthy", exc_info=exc)

        # fallback — выполнить принудительную проверку
        try:
            return self.force_check()
        except Exception as exc:
            self._logger.exception("force_check failed in is_healthy", exc_info=exc)
            return False
