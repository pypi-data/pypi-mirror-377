import unittest
import os

from delta.vcs.handler.delta_git_handler import DeltaGitHandler, DeltaException


class TestCommands(unittest.TestCase):

    def test_commit_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.commit('message')

    def test_add_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.add(['file1', 'file2'])

    def test_pull_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.pull('origin')

    def test_push_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.push('origin')

    def test_fetch_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.fetch('origin')

    def test_create_remote_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.create_remote('origin', 'url')

    def test_status_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.status()

    def test_checkout_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.checkout('new_branch')

    def test_create_tag_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.tag('v0.0.0', 'message')

    def test_push_tag_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.push('origin', 'v0.0.0')

    def test_list_tag_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.list_tag()

    def test_delete_tag_but_not_initialized(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.remove_tag('v1.0.0')

    def test_commit_initialized(self):
        gh = DeltaGitHandler()
        self.assertIsNone(gh.create('test_commit_initialized'))
        first_head = gh._repo.head.commit.hexsha
        self.assertIsNone(gh.commit('Test'))
        second_head = gh._repo.head.commit.hexsha
        self.assertNotEqual(first_head, second_head)

    def test_add_initialized(self):
        gh = DeltaGitHandler()
        gh.create('test_add_initialized')
        open('test_add_initialized/test_add', 'w').close()
        open('test_add_initialized/resources/no_add', 'w').close()
        open('test_add_initialized/models/test_add2', 'w').close()
        res = gh.add(['test_add',
                      'resources/no_add',
                      'models/test_add2'])
        compare = [base_entry[3] for base_entry in res]
        self.assertEqual(compare, ['test_add', 'models/test_add2'])

    def test_fetch_initialized(self):
        gh = DeltaGitHandler()
        self.assertIsNone(gh.create('test_fetch_initialized'))
        with self.assertRaises(DeltaException):
            gh.fetch('origin')
        with self.assertRaises(DeltaException):
            gh.fetch('')

    def test_pull_initialized(self):
        gh = DeltaGitHandler()
        gh.create('test_pull_initialized')
        with self.assertRaises(DeltaException):
            gh.pull('origin')
        with self.assertRaises(DeltaException):
            gh.pull('')

    def test_push_initialized(self):
        gh = DeltaGitHandler()
        gh.create('test_push_initialized')
        with self.assertRaises(DeltaException):
            gh.push('origin')
        with self.assertRaises(DeltaException):
            gh.push('')

    def test_tag_initialized(self):
        gh = DeltaGitHandler()
        self.assertIsNone(gh.create('test_tag_initialized'))
        self.assertIsNone(gh.set_config('test', 'test@toto.org'))

        res = gh.tag('v1.0.0', 'First version')
        self.assertEqual('v1.0.0', res)

        with self.assertRaises(DeltaException):
            gh.tag('v1.0.0', 'First fake version')

        with self.assertRaises(DeltaException):
            gh.push('origin', 'v1.0.0')
        with self.assertRaises(DeltaException):
            gh.push('', 'v1.0.0')

        res = gh.tag('v1.0.1', 'New version')
        self.assertEqual(['v1.0.0', 'v1.0.1'], gh.list_tag())
        gh.remove_tag('v1.0.0')
        self.assertEqual(['v1.0.1'], gh.list_tag())

        with self.assertRaises(DeltaException):
            gh.remove_tag('v1.0.0')
        self.assertEqual(['v1.0.1'], gh.list_tag())
        gh.remove_tag('v1.0.1')
        self.assertEqual([], gh.list_tag())

    def test_checkout_initialized(self):
        gh = DeltaGitHandler()
        gh.create('test_checkout_initialized')
        gh.checkout('toto')
        self.assertEqual('toto', gh._repo.active_branch.name)
        gh.checkout('tata')
        self.assertEqual('tata', gh._repo.active_branch.name)
        gh.checkout('toto')
        self.assertEqual('toto', gh._repo.active_branch.name)

    def test_branch(self):
        gh = DeltaGitHandler()
        with self.assertRaises(DeltaException):
            gh.branch('toto')

        with self.assertRaises(DeltaException):
            gh.list_branches()

        gh.create('test_branch')
        branches = gh.list_branches()
        self.assertEqual(['master'], branches)

        with self.assertRaises(DeltaException):
            gh.remove_branch('toto')

        gh.branch('toto')
        self.assertNotEqual(gh._repo.active_branch.name, 'toto')
        branches = gh.list_branches()
        self.assertEqual(['master', 'toto'], branches)

        gh.remove_branch('toto')
        branches = gh.list_branches()
        self.assertEqual(['master'], branches)

        gh.checkout('abc')
        gh.checkout('toto')
        branches = gh.list_branches()
        self.assertEqual(['abc', 'master', 'toto'], branches)
