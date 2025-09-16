import json
import logging
import typing as tp
from threading import Lock

from .base import ICache


class RedisCache(ICache):
    def __init__(self, client, ttl: int = 60, prefix: str = "celery_health_"):
        self.client = client
        self._ttl = int(ttl)
        self._prefix = prefix
        self._lock = Lock()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _make_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def get(self, key: str) -> tp.Optional[tp.Tuple[bool, float, tp.Optional[str]]]:
        full_key = self._make_key(key)
        try:
            raw = self.client.get(full_key)
            if not raw:
                return None
            # raw may be bytes
            if isinstance(raw, bytes):
                raw = raw.decode('utf-8')
            data = json.loads(raw)
            return bool(data.get('value')), float(data.get('latency', 0.0)), data.get('error')
        except Exception as exc:
            self._logger.warning("Redis get error", exc_info=exc)
            return None

    def set(self, key: str, value: bool, latency: float, error: tp.Optional[str]) -> None:
        full = self._make_key(key)
        try:
            payload = json.dumps({
                "value": bool(value),
                "latency": float(latency),
                "error": error
            })
            # guard with lock to preserve ordering if multiple threads use same client
            with self._lock:
                # use ex (seconds) compatible with redis-py
                self.client.set(full, payload, ex=self._ttl)
        except Exception as exc:
            self._logger.warning("Redis set error", exc_info=exc)
