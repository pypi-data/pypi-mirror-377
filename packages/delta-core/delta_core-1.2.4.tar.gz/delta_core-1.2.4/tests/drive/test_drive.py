import unittest
import os

from delta.drive import DeltaDrive, DeltaTypeError, DeltaIllegalError
from delta.drive.interfaces import IDrive


class TestDrive(unittest.TestCase):

    def test_drive_tag(self):
        drive = DeltaDrive()
        with self.assertRaises(DeltaTypeError):
            drive.init(10)
        drive.init('test_drive_tag')
        drive.repo_directory = 'test_drive_tag'
        tags = drive.tag(list_tags=True, delete=True)
        self.assertEqual([], tags)
        with self.assertRaises(DeltaTypeError):
            drive.tag(tag_name=1)
        with self.assertRaises(DeltaTypeError):
            drive.tag(tag_name=None)
        with self.assertRaises(DeltaIllegalError):
            drive.tag(tag_name='')

        drive.tag(tag_name="toto")
        tags = drive.tag(list_tags=True)
        self.assertEqual(['toto'], tags)
        with self.assertRaises(DeltaTypeError):
            drive.tag(tag_name="toto", delete='error')
        drive.tag(tag_name="toto", delete=True)

    def test_drive_commit(self):
        drive = DeltaDrive()
        drive.init('test_drive_commit')
        drive.repo_directory = 'test_drive_commit'
        with self.assertRaises(DeltaTypeError):
            drive.commit(1)
        with self.assertRaises(DeltaIllegalError):
            drive.commit('')
        drive.commit('Hello world!')

    def test_drive_pull(self):
        drive = DeltaDrive()
        drive.init('test_drive_pull')
        drive.repo_directory = 'test_drive_pull'
        with self.assertRaises(DeltaTypeError):
            drive.pull(1)
        try:
            drive.pull()
        except Exception:
            pass

    def test_drive_push(self):
        drive = DeltaDrive()
        drive.init('test_drive_push')
        drive.repo_directory = 'test_drive_push'
        with self.assertRaises(DeltaTypeError):
            drive.push(remote=1, ref_name=1)
        with self.assertRaises(DeltaTypeError):
            drive.push(remote='toto', ref_name=1)
        try:
            drive.push(remote='toto', ref_name='test')
        except Exception:
            pass

    def test_drive_branch(self):
        drive = DeltaDrive()
        drive.init('test_drive_branch')
        drive.repo_directory = 'test_drive_branch'
        branches = drive.branch()
        self.assertEqual(['master'],  branches)
        with self.assertRaises(DeltaTypeError):
            drive.branch(branch_name=1, delete=True)
        with self.assertRaises(DeltaTypeError):
            drive.branch(branch_name="toto", delete=1)
        drive.branch(branch_name='toto')
        self.assertEqual(['master', 'toto'], drive.branch())
        drive.branch(branch_name='toto', delete=True)
        self.assertEqual(['master'], drive.branch())

    def test_drive_checkout(self):
        drive = DeltaDrive()
        drive.init('test_drive_checkout')
        drive.repo_directory = 'test_drive_checkout'
        self.assertEqual(['master'], drive.branch())
        with self.assertRaises(DeltaTypeError):
            drive.checkout(1)
        drive.checkout('toto')
        self.assertEqual(['master', 'toto'], drive.branch())

    def test_drive_reset(self):
        drive = DeltaDrive()
        drive.init('test_drive_reset')
        drive.repo_directory = 'test_drive_reset'
        drive.reset()

    def test_drive_add_dependency(self):
        drive = DeltaDrive()
        drive.init('test_drive_add_dependency')
        drive.repo_directory = 'test_drive_add_dependency'
        drive.add_dependency()

    def test_drive_add_resource(self):
        drive = DeltaDrive()
        drive.init('test_drive_add_resource')
        drive.repo_directory = 'test_drive_add_resource'
        with self.assertRaises(Exception):
            drive.add_resource(name=1, path='./goodurl/test', download=True)
        with self.assertRaises(Exception):
            drive.add_resource(name='resource_name', path=1, download=True)

    def test_drive_check(self):
        drive = DeltaDrive()
        drive.init('test_drive_check')
        drive.repo_directory = 'test_drive_check'
        self.assertTrue(drive.check())

    def test_drive_fetch(self):
        drive = DeltaDrive()
        drive.init('test_drive_fetch')
        drive.repo_directory = 'test_drive_fetch'
        with self.assertRaises(DeltaTypeError):
            drive.fetch(1)
        try:
            drive.fetch('origin')
        except Exception:
            pass

    def test_drive_interface(self):
        drive = IDrive()
        with self.assertRaises(NotImplementedError):
            drive.add_dependency()

        with self.assertRaises(NotImplementedError):
            drive.add_resource()

        with self.assertRaises(NotImplementedError):
            drive.branch()

        with self.assertRaises(NotImplementedError):
            drive.branch(branch_name='toto')

        with self.assertRaises(NotImplementedError):
            drive.branch(branch_name='toto', delete=True)

        with self.assertRaises(NotImplementedError):
            drive.check()

        with self.assertRaises(NotImplementedError):
            drive.checkout('branch')

        with self.assertRaises(NotImplementedError):
            drive.clone('url', 'path')

        with self.assertRaises(NotImplementedError):
            drive.commit('message')

        with self.assertRaises(NotImplementedError):
            drive.fetch('origin')

        with self.assertRaises(NotImplementedError):
            drive.init('path')

        with self.assertRaises(NotImplementedError):
            drive.pull('origin')

        with self.assertRaises(NotImplementedError):
            drive.push()

        with self.assertRaises(NotImplementedError):
            drive.reset()

        with self.assertRaises(NotImplementedError):
            drive.status()

        with self.assertRaises(NotImplementedError):
            drive.sync()

        with self.assertRaises(NotImplementedError):
            drive.tag()

    def test_execute_git_command(self):
        _, status = DeltaDrive.execute_git_command(
            "init",
            "test_execute_git_command")
        self.assertEqual(0, status)
        _, status = DeltaDrive.execute_git_command(
            "checkout",
            "-b",
            "toto",
            path="test_execute_git_command")
        self.assertEqual(0, status)

        _, status = DeltaDrive.execute_git_command(
            "not",
            "a",
            "git",
            "command")
        self.assertEqual(1, status)

        _, status = DeltaDrive.execute_git_command(
            "not",
            "a",
            "git",
            "command",
            path="test_execute_git_command")
        self.assertEqual(1, status)

        with self.assertRaises(TypeError):
            DeltaDrive.execute_git_command(
                "not",
                "a",
                "git",
                "command",
                path=1)
