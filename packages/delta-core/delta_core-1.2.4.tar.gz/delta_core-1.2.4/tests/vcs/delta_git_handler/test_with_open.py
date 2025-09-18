import unittest
import os

from delta.vcs.handler.delta_git_handler import DeltaGitHandler, DeltaException


class TestWithOpen(unittest.TestCase):

    def test_with_open(self):
        with DeltaGitHandler() as repo:
            repo.create('test_with_open')
            self.assertIsNotNone(repo._repo)
            path = os.path.join(
                os.path.abspath('.'),
                'test_with_open')
            self.assertTrue(repo._path == path)
            self.assertTrue(repo._initialize_flag)
