import logging
import os
from typing import Any

from delta.drive import DeltaDrive
from delta.manifest.manifest import read_manifest
from delta.runners.factory import create
from delta.vcs.handler import GitlabAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Delta")


class DeltaCore:
    def __init__(self):
        """
        TODO: Need to change IDrive and IRun
        => Need a real instance.
        """
        self._drive = DeltaDrive()
        self._run = None

    def drive_clone(self, url: str, path_to_save: str = "."):
        self._drive.clone(url, path_to_save)

    def drive_init(self, path_to_save: str):
        self._drive.init(path_to_save)

    def drive_status(self):
        self._drive.status()

    def drive_tag(self, **kwargs):
        return self._drive.tag(**kwargs)

    def drive_commit(self, message: str):
        self._drive.commit(message)

    def drive_pull(self, origin_name: str = ""):
        self._drive.pull(origin_name)

    def drive_push(self, **kwargs):
        self._drive.push(**kwargs)

    def drive_branch(self, branch_name: str = None, delete: bool = False):
        """
        Create/Remove branch
        """
        if branch_name is None or branch_name == "":
            return self._drive.branch()
        else:
            self._drive.branch(branch_name=branch_name, delete=delete)

    def drive_checkout(self, branch_name: str):
        self._drive.checkout(branch_name)

    def drive_reset(self):
        self._drive.reset()

    def drive_add_dependency(self):
        self._drive.add_dependency()

    def drive_add_resource(self, **kwargs):
        self._drive.add_resource(**kwargs)
        logger.info("A resource has been added.")

    def drive_delete_resource(self, **kwargs):
        self._drive.delete_resource(**kwargs)

    def drive_get_resources(self):
        return self._drive.get_resources()

    def drive_check(self):
        return self._drive.check()

    def drive_fetch(self, origin_name: str = ""):
        self._drive.fetch(origin_name)

    def drive_sync(self):
        self._drive.sync()

    def run_configure(self, **kwargs):
        if self._run is None:
            logger.warning("Need a run instance to configure the runner.")
            return
        _manifest = read_manifest(
            os.path.join(self._drive.repo_directory, "manifest.json")
        )
        kwargs["resources"] = _manifest["resources"]
        self._run.configure(**kwargs)

    def run_start(self, **kwargs):
        if self._run is None:
            _manifest = read_manifest(
                os.path.join(self._drive.repo_directory, "manifest.json")
            )
            self._run = create(_manifest["models"])
            kwargs["resources"] = _manifest["resources"]
        logger.info("Job runner is starting...")
        self._run.start(**kwargs)
        logger.info("Done.")

    def run_stop(self, **kwargs):
        if self._run is None:
            _manifest = read_manifest(
                os.path.join(self._drive.repo_directory, "manifest.json")
            )
            self._run = create(_manifest["models"])
        logger.info("Stopping runner...")
        self._run.stop(**kwargs)
        logger.info("Done.")

    def run_resume(self, **kwargs):
        if self._run is None:
            logger.warning("Cannot resume, need to start before.")
            return
        _manifest = read_manifest(
            os.path.join(self._drive.repo_directory, "manifest.json")
        )
        kwargs["resources"] = _manifest["resources"]
        self._run.resume(**kwargs)

    def run_monitor(self, **kwargs):
        if self._run is None:
            logger.warning("Need an instance to monitor the runner.")
            return
        _manifest = read_manifest(
            os.path.join(self._drive.repo_directory, "manifest.json")
        )
        kwargs["resources"] = _manifest["resources"]
        self._run.monitor(**kwargs)

    def list(self, url, private_token):
        with GitlabAPI(url, private_token) as glapi:
            glapi.get_projects()

    def drive_build(self, version, registry, no_cache=False):
        self._drive.docker_build(
            version=version, registry=registry, no_cache=no_cache
        )

    def set_verbosity_level(self, verbose_level):
        logger.setLevel(verbose_level)

    def close(self):
        pass

    def __enter__(self) -> "DeltaCore":
        return self

    def __exit__(self, *args: Any, **kwargs) -> None:
        self.close()
