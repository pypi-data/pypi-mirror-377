import unittest
import os

from delta.core import DeltaCore
from delta.vcs.handler import DeltaGitHandler


class FakeRun:
    def configure(**kwargs):
        pass

    def run(**kwargs):
        pass

    def monitor(**kwargs):
        pass

    def stop(**kwargs):
        pass

    def resume(**kwargs):
        pass


class TestCoreRun(unittest.TestCase):
    def test_run_start_initialized(self):
        with DeltaCore() as core:
            try:
                core._run = FakeRun()
                kwargs = {

                }
                core.run_start(**kwargs)
            except Exception:
                pass

    def test_run_stop_initialized(self):
        with DeltaCore() as core:
            try:
                core._run = FakeRun()
                kwargs = {

                }
                core.run_stop(**kwargs)
            except Exception:
                pass

    def test_run_resume_initialized(self):
        with DeltaCore() as core:
            try:
                core._run = FakeRun()
                kwargs = {

                }
                core.run_resume(**kwargs)
            except Exception:
                pass

    def test_run_monitor_initialized(self):
        with DeltaCore() as core:
            try:
                core._run = FakeRun()
                kwargs = {

                }
                core.run_monitor(**kwargs)
            except Exception:
                pass

    def test_run_configure_initialized(self):
        with DeltaCore() as core:
            core._run = FakeRun()
            try:
                kwargs = {

                }
                core.run_configure(**kwargs)
            except Exception:
                pass

    def test_run_start_not_initialized(self):
        with DeltaCore() as core:
            try:
                kwargs = {

                }
                core.run_start(**kwargs)
            except Exception:
                pass

    def test_run_stop_not_initialized(self):
        with DeltaCore() as core:
            try:
                kwargs = {

                }
                core.run_stop(**kwargs)
            except Exception:
                pass

    def test_run_resume_not_initialized(self):
        with DeltaCore() as core:
            try:
                kwargs = {

                }
                core.run_resume(**kwargs)
            except Exception:
                pass

    def test_run_monitor_not_initialized(self):
        with DeltaCore() as core:
            try:
                kwargs = {

                }
                core.run_monitor(**kwargs)
            except Exception:
                pass

    def test_run_configure_not_initialized(self):
        with DeltaCore() as core:
            try:
                kwargs = {

                }
                core.run_configure(**kwargs)
            except Exception:
                pass
