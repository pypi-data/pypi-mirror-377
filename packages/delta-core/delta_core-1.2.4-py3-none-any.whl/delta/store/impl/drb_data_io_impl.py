from delta.store.interfaces import IData
from delta.store.interfaces import IDataIO
import drb.core.signature
from drb.topics import resolver
import io


class DrbDataIOImpl(IDataIO):
    def __init__(self, src: IData, dst=None):
        super().__init__(src, dst)

    def _read(self):
        path = self._src.info['path']
        drb_node = resolver.create(path)
        if drb_node.has_impl(io.BufferedIOBase):
            return drb_node.get_impl(io.BufferedIOBase)
        if drb_node.has_impl(io.BytesIO):
            return drb_node.get_impl(io.BytesIO)
        raise TypeError("DRB Impl not supported...")

    def _write(self, data):
        self._dst.write(data.read())
