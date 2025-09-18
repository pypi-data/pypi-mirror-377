import os
import logging
from delta.store.interfaces import IData
from delta.store.interfaces import IStore
from delta.store.impl.drb_data_io_impl import DrbDataIOImpl
from delta.store.impl.fetcher_all_impl import FetcherAllImpl

from delta.manifest import manifest

logger = logging.getLogger('Delta')


class StoreImpl(IStore):

    def _write_on_manifest(self, name, path):
        """
        Write resource to manifest
        """
        if not os.path.exists('manifest.json'):
            manifest.write_manifest()
        _manifest = manifest.read_manifest()

        if "resources" not in _manifest:
            _manifest["resources"] = {
                "path": "resources",
                "items": []
            }

        items = _manifest["resources"]["items"]
        names = [item["name"] for item in items]

        if name not in names:
            json = {
                "name": name,
                "source_url": path
            }
            logger.info("Updating the manifest...")
            _manifest["resources"]["items"].append(json)
            manifest.write_manifest(content=_manifest)

    def add_resource(self, resources_path: str = './resources', **kwargs):
        """
        Add a resource to manifest and resources folder.
        So it will fetch data and write file to resources folder.

        :Keyword Arguments:
        * *name* (``str``) --
            Resource name.
        * *path* (``str``) --
            Data where we can find the resource file.
        * *download* (``boolean``) --
            A boolean that tell if the data will be downloaded
            in the resources folder.
        """
        data = IData()
        data_name = kwargs.get('name')
        data_path = kwargs.get('path')
        download = kwargs.get('download')
        data.add_info(name=data_name, path=data_path)

        if not os.path.exists(resources_path):
            try:
                os.makedirs(resources_path, exist_ok=True)
            except OSError:
                logger.warning(
                    f"WARNING: Failed to create {resources_path}...")

        if download:
            file_path = os.path.abspath(
                os.path.join(resources_path, data_name))
            with open(file_path, 'wb') as resource:
                drb_dataIO = DrbDataIOImpl(data, resource)
                fetcher = FetcherAllImpl(drb_dataIO)
                logger.info(f"Fetching {data_path}...")
                fetcher.fetch()
                logger.info(f"INFO: {data_path} has been fetched.")

        self._write_on_manifest(data_name, data_path)

    def remove_resource(self, **kwargs):
        """
        Remove a resource entry from the manifest.

        :Keyword Arguments:
        * *name* (``str``) --
            Resource name.
        """

        data_name = kwargs.get('name')

        if not os.path.exists('manifest.json'):
            logger.info("No manifest found")
            return

        _manifest = manifest.read_manifest()

        if "resources" not in _manifest:
            logger.info("INFO: No resource entry found")
            return

        for item in _manifest['resources']['items']:
            if item['name'] == data_name:
                _manifest['resources']['items'].remove(item)
                logger.info(
                    f"INFO: The resource {data_name} has been deleted.")

        manifest.write_manifest(content=_manifest)

    def get_resources(self):
        if not os.path.exists('manifest.json'):
            logger.info("No manifest found")
            return

        _manifest = manifest.read_manifest()

        if "resources" not in _manifest:
            logger.info("INFO: No resource entry found")
            return

        return _manifest['resources']['items']
