from abc import ABC, abstractmethod


class IStore(ABC):
    @abstractmethod
    def add_resource(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def remove_resource(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_resources(self):
        raise NotImplementedError()
