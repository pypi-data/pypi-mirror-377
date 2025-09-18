import unittest
import os

from delta.vcs.handler.delta_git_handler import DeltaGitHandler, DeltaException


class TestLoadLocalRepo(unittest.TestCase):
    def test_load_not_local_repo(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.load_local_repo('test_load_not_local_repo_')
        self.assertTrue(gh._repo is None)
        self.assertTrue(gh._path is None)
        self.assertTrue(gh._initialize_flag is False)

    def test_load_local_repo(self):
        gh = DeltaGitHandler()
        self.assertIsNone(gh.create('test_load_local_repo1'))
        self.assertIsNone(gh.create('test_load_local_repo2'))
        self.assertIsNotNone(gh._repo)
        self.assertEqual(
            gh._path,
            os.path.join(
                os.path.abspath('.'),
                'test_load_local_repo2'
                )
            )
        self.assertTrue(gh._initialize_flag is True)

        self.assertIsNone(gh.load_local_repo('test_load_local_repo1'))

        self.assertIsNotNone(gh._repo)
        self.assertEqual(gh._path,
                         os.path.join(os.path.abspath('.'),
                                      'test_load_local_repo1'))
        self.assertTrue(gh._initialize_flag is True)
