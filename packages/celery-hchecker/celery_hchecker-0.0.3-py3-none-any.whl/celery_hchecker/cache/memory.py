import typing as tp
from threading import Lock

from cachetools import TTLCache

from .base import ICache


class MemoryCache(ICache):
    def __init__(self, maxsize: int = 1000, ttl: int = 60):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = Lock()

    def get(self, key: str) -> tp.Optional[tp.Tuple[bool, float, tp.Optional[str]]]:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: bool, latency: float, error: tp.Optional[str]) -> None:
        with self._lock:
            self._cache[key] = (value, latency, error)
