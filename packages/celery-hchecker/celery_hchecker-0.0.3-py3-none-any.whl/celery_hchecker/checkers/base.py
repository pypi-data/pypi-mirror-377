import typing as tp
from abc import ABC, abstractmethod


class IChecker(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def check(self) -> tp.Tuple[bool, float, tp.Optional[str]]:
        """Возвращает (успех, latency в секундах, текст ошибки)"""
        ...
