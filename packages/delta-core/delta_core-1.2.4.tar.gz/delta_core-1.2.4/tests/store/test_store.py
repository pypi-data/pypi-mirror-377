import unittest

from delta.store.impl import StoreImpl
from delta.manifest import manifest
import os

RESOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'resources')


class TestStore(unittest.TestCase):
    def test_add_resource(self):
        store = StoreImpl()
        store.add_resource(resources_path=RESOURCE_DIR,
                           name="drb.zip",
                           path="https://gitlab.com/drb-python/drb/"
                           "-/archive/main/drb-main.zip")
        _manifest = manifest.read_manifest()
        self.assertEqual(_manifest['resources']['items'][0]["name"], 'drb.zip')
        self.assertEqual(
            _manifest['resources']['items'][0]["source_url"],
            "https://gitlab.com/drb-python/drb/""-/archive/main/drb-main.zip")
        self.assertFalse(os.path.exists(os.path.join(
            RESOURCE_DIR, "drb.zip"
        )))
        self.assertEqual(store.get_resources()[0]['name'], 'drb.zip')
        store.remove_resource(name='drb.zip')
        self.assertEqual(len(store.get_resources()), 0)
        store.add_resource(resources_path=RESOURCE_DIR,
                           name="drb.zip",
                           path="https://gitlab.com/drb-python/drb/"
                           "-/archive/main/drb-main.zip",
                           download=True)
        _manifest = manifest.read_manifest()
        self.assertEqual(_manifest['resources']['items'][0]["name"], 'drb.zip')
        self.assertEqual(
            _manifest['resources']['items'][0]["source_url"],
            "https://gitlab.com/drb-python/drb/""-/archive/main/drb-main.zip")
        self.assertTrue(os.path.exists(os.path.join(
            RESOURCE_DIR, "drb.zip"
        )))
