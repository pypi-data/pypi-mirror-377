import typing as tp
from abc import ABC, abstractmethod


class ICache(ABC):
    """Абстракция для кеширования результатов проверок"""

    @abstractmethod
    def get(self, key: str) -> tp.Optional[tp.Tuple[bool, float, tp.Optional[str]]]:
        ...

    @abstractmethod
    def set(self, key: str, value: bool, latency: float, error: tp.Optional[str]) -> None:
        ...
