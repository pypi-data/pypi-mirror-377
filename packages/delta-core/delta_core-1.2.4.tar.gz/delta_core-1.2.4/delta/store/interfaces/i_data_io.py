from abc import ABC, abstractmethod
from typing import TypeVar
from .i_data import IData

T = TypeVar('T')


class IDataIO(ABC):
    def __init__(self, src: IData, dst=None):
        self._src = src
        self._dst = dst

    @abstractmethod
    def _read(self) -> T:
        raise NotImplementedError()

    @abstractmethod
    def _write(self, data: T):
        raise NotImplementedError()
