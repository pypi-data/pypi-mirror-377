import unittest
import os

from delta.core import DeltaCore
from delta.vcs.handler import DeltaGitHandler


class TestCoreDrive(unittest.TestCase):
    def test_drive_clone(self):
        with DeltaCore() as core:
            try:
                core.drive_clone('toto')
            except Exception:
                pass

    def test_core_drive_init(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_init')
            self.assertTrue(os.path.exists('test_core_drive_init'))

    def test_core_drive_status(self):
        with DeltaCore() as core:
            core.drive_status()

    def test_core_drive_tag(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_tag')
            core._drive.repo_directory = 'test_core_drive_tag'
            self.assertEqual([], core.drive_tag(list_tags=True))
            core.drive_tag(tag_name='v1.0.0')
            self.assertEqual(['v1.0.0'], core.drive_tag(list_tags=True))
            core.drive_tag(tag_name='v1.0.0',
                           delete=True,
                           message='Hello World!')
            self.assertEqual([], core.drive_tag(list_tags=True))

    def test_core_drive_commit(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_commit')
            core._drive.repo_directory = 'test_core_drive_commit'
            core.drive_commit("Hello World!")
            with DeltaGitHandler() as repo:
                repo.load_local_repo('test_core_drive_commit')
                self.assertEqual(repo._repo.head.commit.message,
                                 "Hello World!")

    def test_core_drive_pull(self):
        with DeltaCore() as core:
            try:
                core.drive_init('test_core_drive_pull')
                core._drive.repo_directory = 'test_core_drive_pull'
                core.drive_pull()
            except Exception:
                pass

    def test_core_drive_push(self):
        with DeltaCore() as core:
            try:
                core.drive_init('test_core_drive_push')
                core._drive.repo_directory = 'test_core_drive_push'
                core.drive_push()
            except Exception:
                pass

    def test_core_drive_branch(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_branch')
            core._drive.repo_directory = 'test_core_drive_branch'
            branches = core.drive_branch()
            self.assertEqual(['master'], branches)
            core.drive_branch(branch_name='toto')
            branches = core.drive_branch()
            self.assertEqual(['master', 'toto'], branches)
            core.drive_branch(branch_name='toto', delete=True)
            branches = core.drive_branch()
            self.assertEqual(['master'], branches)

    def test_core_drive_checkout(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_checkout')
            core._drive.repo_directory = 'test_core_drive_checkout'
            branches = core.drive_branch()
            self.assertEqual(['master'], branches)
            core.drive_checkout('toto')
            branches = core.drive_branch()
            self.assertEqual(['master', 'toto'], branches)
            with self.assertRaises(Exception):
                core.drive_branch(branch_name='toto', delete=True)
            core.drive_checkout('master')
            core.drive_branch(branch_name='toto', delete=True)
            branches = core.drive_branch()
            self.assertEqual(['master'], branches)

    def test_core_drive_reset(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_reset')
            core._drive.repo_directory = 'test_core_drive_reset'
            core.drive_reset()

    def test_core_drive_add_dependency(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_add_dependency')
            core._drive.repo_directory = 'test_core_drive_add_dependency'
            core.drive_add_dependency()

    def test_core_drive_add_resource(self):
        with DeltaCore() as core:
            try:
                core.drive_init('test_core_drive_add_resource')
                core._drive.repo_directory = 'test_core_drive_add_resource'
                core.drive_add_resource(name="toto", path="goodurl/toto")
            except Exception:
                pass

    def test_core_drive_check(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_check')
            core._drive.repo_directory = 'test_core_drive_check'
            self.assertTrue(core.drive_check())

    def test_core_drive_fetch(self):
        with DeltaCore() as core:
            try:
                core.drive_init('test_core_drive_fetch')
                core._drive.repo_directory = 'test_core_drive_fetch'
                core.drive_fetch()
            except Exception:
                pass

    def test_core_drive_sync(self):
        with DeltaCore() as core:
            core.drive_init('test_core_drive_sync')
            core._drive.repo_directory = 'test_core_drive_sync'
            core.drive_sync()
