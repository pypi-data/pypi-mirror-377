import unittest
import os

from delta.vcs.handler.delta_git_handler import DeltaGitHandler, DeltaException


class TestCloneRepo(unittest.TestCase):

    def test_clone_not_https_or_ssh_url(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.clone('toto', '.')
        self.assertTrue(gh._repo is None)
        self.assertTrue(gh._path is None)
        self.assertTrue(gh._initialize_flag is False)

    def test_clone_https_url_but_not_a_repo(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.clone('https://git.gael.fr/', '.')
        self.assertTrue(gh._repo is None)
        self.assertTrue(gh._path is None)
        self.assertTrue(gh._initialize_flag is False)

    def test_clone_https(self):
        gh = DeltaGitHandler()
        self.assertIsNone(
            gh.clone('https://gitlab.com/drb-python/drb.git', '.'))
        self.assertIsNotNone(gh._repo)
        self.assertEqual(gh._path, os.path.join(os.path.abspath('.'), 'drb'))
        self.assertTrue(gh._initialize_flag is True)
