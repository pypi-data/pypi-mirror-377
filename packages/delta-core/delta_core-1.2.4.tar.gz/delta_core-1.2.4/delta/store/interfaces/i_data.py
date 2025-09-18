from abc import ABC


class IData(ABC):
    # Contient source et dest
    def __init__(self):
        self._info: dict = {}

    @property
    def info(self) -> dict:
        return self._info

    def add_info(self, **kwargs):
        for key, value in kwargs.items():
            self._info[key] = value

    def remove_info(self, key):
        return self._info.pop(key, None)
