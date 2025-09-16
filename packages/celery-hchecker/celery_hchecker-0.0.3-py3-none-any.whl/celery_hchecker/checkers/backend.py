import logging
import time
import typing as tp
import uuid

from celery.backends.base import BaseBackend

from .base import IChecker


class BackendChecker(IChecker):
    def __init__(self, backend: BaseBackend, cleanup: bool = True, timeout: float = 5.0, wait: float = 1.0):
        self._backend = backend
        self._cleanup = cleanup
        self._timeout = timeout
        self._wait = wait  # max time to poll for result
        self._logger = logging.getLogger(self.__class__.__name__)

    def _make_key(self) -> str:
        return f"health_{uuid.uuid4().hex}"

    def name(self) -> str:
        return 'backend'

    def check(self) -> tp.Tuple[bool, float, tp.Optional[BaseException]]:
        key = self._make_key()
        start = time.monotonic()
        try:
            # gentle attempt to set backend timeout if supported
            if hasattr(self._backend, 'timeout'):
                try:
                    self._backend.timeout = self._timeout
                except Exception:
                    pass

            self._backend.store_result(key, 'OK', state='SUCCESS')

            # poll get_task_meta until we see result or timeout
            deadline = start + self._wait
            meta = None
            while time.monotonic() < deadline:
                meta = self._backend.get_task_meta(key) or {}
                # meta may include 'result' or 'state'
                result = meta.get('result', None)
                state = meta.get('status') or meta.get('state')
                if result == 'OK' or state == 'SUCCESS':
                    latency = time.monotonic() - start
                    return True, latency, None
                time.sleep(0.05)
            raise RuntimeError(f"Timeout waiting for backend meta: {meta}")
        except Exception as exc:
            latency = time.monotonic() - start
            self._logger.error("Backend check failed", exc_info=exc)
            return False, latency, exc
        finally:
            if self._cleanup:
                try:
                    if hasattr(self._backend, 'delete'):
                        self._backend.delete(key)
                except Exception as exc:
                    self._logger.warning("Cleanup error", exc_info=exc)
