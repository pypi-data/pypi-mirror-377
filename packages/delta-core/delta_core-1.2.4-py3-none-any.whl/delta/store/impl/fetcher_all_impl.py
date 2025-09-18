from delta.store.interfaces import IFetcher
from delta.store.interfaces import IDataIO


class FetcherAllImpl(IFetcher):
    def __init__(self, dataIO: IDataIO):
        super().__init__(dataIO)

    def fetch(self):
        """
        Read and write data using DataIO.
        """
        data = self._dataIO._read()
        self._dataIO._write(data)
