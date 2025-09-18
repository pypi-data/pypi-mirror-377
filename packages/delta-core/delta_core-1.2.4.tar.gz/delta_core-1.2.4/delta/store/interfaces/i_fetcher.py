from abc import ABC, abstractmethod
from typing import TypeVar

from .i_data_io import IDataIO

T = TypeVar('T')


class IFetcher(ABC):

    def __init__(self, dataIO: IDataIO):
        self._dataIO = dataIO

    @abstractmethod
    def fetch(self) -> T:
        raise NotImplementedError()
