import logging
import time
import typing as tp

from celery import Celery

from .base import IChecker


class WorkersChecker(IChecker):
    def __init__(self, app: Celery, timeout: float = 5.0, retries: int = 3, delay: float = 0.5):
        self.app = app
        self.timeout = timeout
        self.retries = retries
        self.delay = delay

        self._logger = logging.getLogger(self.__class__.__name__)

    def name(self) -> str:
        return 'workers'

    def check(self) -> tp.Tuple[bool, float, tp.Optional[str]]:
        start = time.monotonic()
        last_error = None
        for i in range(1, self.retries + 1):
            try:
                inspect = self.app.control.inspect(timeout=self.timeout)
                ping = inspect.ping() or {}
                active = inspect.active() or {}
                if not ping or not any(active.values()):
                    raise RuntimeError("No active workers or no ping")
                latency = time.monotonic() - start
                return True, latency, None
            except Exception as e:
                last_error = str(e)
                self._logger.warning(f"Workers attempt {i} failed: {e}")
                time.sleep(self.delay * i)

        latency = time.monotonic() - start
        return False, latency, last_error
