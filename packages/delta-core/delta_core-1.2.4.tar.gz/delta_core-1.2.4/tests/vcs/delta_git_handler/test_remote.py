import unittest
from delta.vcs.handler.delta_git_handler import DeltaGitHandler, DeltaException


class TestRemote(unittest.TestCase):
    def test_remote_list(self):
        gh = DeltaGitHandler()
        gh.create('test_remote_list')
        gh.create_remote('origin', 'afakeurlwhichnormallydontwork.com')
        self.assertEqual(gh.list_remotes(), ['origin'])

        gh.create_remote('toto', 'afakeurlwhichnormallydontwork2.com')

        self.assertEqual(gh.list_remotes(), ['origin', 'toto'])

    def test_remote_list_empty(self):
        gh = DeltaGitHandler()
        gh.create('test_remote_list_empty')
        self.assertEqual(gh.list_remotes(), [])

    def test_remote_list_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.list_remotes()
