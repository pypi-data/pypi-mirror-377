import unittest

from delta.vcs.handler.delta_git_handler import DeltaGitHandler


class TestClose(unittest.TestCase):
    def test_close(self):
        gh = DeltaGitHandler()
        gh._path = 'test'
        gh._initialize_flag = True
        gh.close()
        self.assertEqual(gh._path, None)
        self.assertEqual(gh._initialize_flag, False)
