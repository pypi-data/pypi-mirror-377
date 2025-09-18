import unittest
import os

from delta.core import DeltaCore
from delta.vcs.handler import DeltaGitHandler


class TestCore(unittest.TestCase):
    def test_list(self):
        with DeltaCore() as core:
            try:
                core.list('url', 'token')
            except Exception:
                pass
