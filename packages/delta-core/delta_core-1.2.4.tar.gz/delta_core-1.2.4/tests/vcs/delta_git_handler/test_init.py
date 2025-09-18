import unittest
import os
from delta.vcs.handler.delta_git_handler import DeltaGitHandler


class TestInit(unittest.TestCase):
    def test_init(self):
        gh = DeltaGitHandler()
        gh.create('test_init')
        self.assertEqual(gh._path, os.path.abspath('test_init'))
        self.assertEqual(gh._initialize_flag, True)
        self.assertIsNotNone(gh._repo)

        self.assertTrue(os.path.exists(os.path.join(
                                            os.path.abspath('test_init'),
                                            'manifest.json')))
        self.assertTrue(os.path.exists(os.path.join(
                                            os.path.abspath('test_init'),
                                            '.delta')))
        self.assertTrue(os.path.exists(os.path.join(
                                            os.path.abspath('test_init'),
                                            'resources')))
        self.assertTrue(os.path.exists(os.path.join(
                                            os.path.abspath('test_init'),
                                            'artifacts')))
        self.assertTrue(os.path.exists(os.path.join(
                                            os.path.abspath('test_init'),
                                            'sources')))
        self.assertTrue(os.path.exists(os.path.join(
                                            os.path.abspath('test_init'),
                                            'models')))
