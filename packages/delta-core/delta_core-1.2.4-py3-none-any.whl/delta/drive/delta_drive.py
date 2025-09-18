import logging
import os
import tarfile
import tempfile
from typing import Callable

import docker
from git import Git

from delta.drive.interfaces import IDrive
from delta.manifest import manifest
from delta.manifest.parser import Model, parse
from delta.run.job.builder import JobBuilder
from delta.run.job.builder.python_builder import PythonRunner
from delta.store.impl import StoreImpl
from delta.vcs.handler import DeltaGitHandler


class DeltaTypeError(Exception):
    pass


class DeltaIllegalError(Exception):
    pass


class DeltaDrive(IDrive):

    def __init__(self):
        self._repo_directory = "."

    @property
    def repo_directory(self):
        return self._repo_directory

    @repo_directory.setter
    def repo_directory(self, directory):
        self._repo_directory = directory

    def clone(self, url: str, path_to_save: str = repo_directory):
        r"""
        Clone a repository.

        :param url:
        URL where the repository is located.
        :type url: ``str``

        :param path_to_save:
        The path where we want to save locally the repository.
        :type path_to_save: ``str``
        """
        if not isinstance(path_to_save, str):
            raise DeltaTypeError("Wrong type for path_to_save. Need a str.")
        with DeltaGitHandler() as repo:
            repo.clone(url, path_to_save)

    def init(self, path_to_save: str):
        r"""
        Initialize a new repository.

        :param path_to_save:
        Path where we want to save locally the repository.
        :type path_to_save: ``str``
        """
        if not isinstance(path_to_save, str):
            raise DeltaTypeError("Wrong type for path_to_save. Need a str.")
        with DeltaGitHandler() as repo:
            repo.create(path_to_save)

    def status(self):
        pass

    def tag(self, **kwargs):
        r"""
        Can remove, list and create tags.

        :Keyword Arguments:
        * *list_tags* (``bool``) --
            Flag to list all tags in repo.
        * *tag_name* (``str``) --
            Tag name needs to be created or removed.
        * *delete* (``bool``) --
            Flag to delete or not the tag.
        * *message* (``str``) --
            Message when we create the new tag.
        """
        list_tags = kwargs.get("list_tags", False)
        if list_tags:
            with DeltaGitHandler() as repo:
                repo.load_local_repo(self.repo_directory)
                return repo.list_tag()
        else:
            tag_name = kwargs.get("tag_name")
            if not isinstance(tag_name, str):
                raise DeltaTypeError("Wrong type for tag_name. Need a str.")
            if tag_name == "":
                raise DeltaIllegalError("Illegal tag name")
            delete = kwargs.get("delete", False)
            if not isinstance(delete, bool):
                raise DeltaTypeError("Wrong type for delete. Need a bool")
            with DeltaGitHandler() as repo:
                repo.load_local_repo(self.repo_directory)
                if delete:
                    repo.remove_tag(tag_name)
                else:
                    message = kwargs.get("message", "")
                    if not isinstance(message, str):
                        raise DeltaTypeError(
                            "Wrong type for message." "Need a str."
                        )
                    repo.tag(tag_name, message)

    def commit(self, message: str):
        r"""
        Save all modification.

        :param message:
        Message associated of the commit.
        :type message: ``str``
        """
        if not isinstance(message, str):
            raise DeltaTypeError("Wrong type for message. Need a str.")
        if message == "":
            raise DeltaIllegalError(
                "Wrong message for your commit. " "Need a non-empty message."
            )
        with DeltaGitHandler() as repo:
            repo.load_local_repo(self.repo_directory)
            repo.commit(message)

    def pull(self, remote_name: str):
        r"""
        Fetch distant references and all modification will
        be integrated by the current local branch.

        :param remote_name:
        Name of the remote.
        :type remote_name: ``str``
        """
        if remote_name is not None:
            if not isinstance(remote_name, str):
                raise DeltaTypeError("Wrong type for remote_name. Need a str.")
        with DeltaGitHandler() as repo:
            repo.load_local_repo(self.repo_directory)
            repo.pull(remote_name)

    def push(self, **kwargs):
        r"""
        Push to origin.
        If no remote has been specified, 'origin' will
        be used by default.

        :param \**kwargs:
        See below

        :Keyword Arguments:
        * *remote* (``str``) --
            Remote name.
        * *ref_name* (``str``) --
            Tag name needs to be pushed.
        """
        remote_name = kwargs.get("remote", None)
        if remote_name is not None:
            if not isinstance(remote_name, str):
                raise DeltaTypeError("Wrong type for origin_name. Need a str.")
        ref_name = kwargs.get("ref_name", None)
        if ref_name is not None:
            if not isinstance(ref_name, str):
                raise DeltaTypeError(
                    "Wrong type for reference name. " "Need a str"
                )
        with DeltaGitHandler() as repo:
            repo.load_local_repo(self.repo_directory)
            repo.push(remote_name, ref_name)

    def branch(self, **kwargs):
        r"""
        List all branches available in a repo.
        Also, create and delete a branch.

        :param \**kwargs:
        See below

        :returns:
        No arguments or there isn't `branch_name`,
        will return a list of all branches available.
        Or return `None`.

        :Keyword Arguments:
        * *branch_name* (``str``) --
            Branch name you want to create or delete.
        * *delete* (``bool``) --
            Flag to delete branch.
        """
        branch_name = kwargs.get("branch_name", None)
        if branch_name is None:
            with DeltaGitHandler() as repo:
                repo.load_local_repo(self.repo_directory)
                return repo.list_branches()
        delete = kwargs.get("delete", False)
        if not isinstance(branch_name, str):
            raise DeltaTypeError("Wrong type for branch_name. Need a str.")
        if not isinstance(delete, bool):
            raise DeltaTypeError("Wrong type for delete. Need a bool.")
        with DeltaGitHandler() as repo:
            repo.load_local_repo(self.repo_directory)
            if delete:
                repo.remove_branch(branch_name)
            else:
                repo.branch(branch_name)

    def checkout(self, ref_name: str):
        r"""
        Switch to a reference of your repo (tag, commit, or branch).

        :param ref_name:
        Name of the reference.
        :type ref_name: ``str``
        """
        if not isinstance(ref_name, str):
            raise DeltaTypeError("Wrong type for ref_name. Need a str.")
        with DeltaGitHandler() as repo:
            repo.load_local_repo(self.repo_directory)
            repo.checkout(ref_name)

    def reset(self):
        pass

    def add_dependency(self):
        pass

    def add_resource(self, **kwargs):
        r"""
        Add a resource to manifest and resources folder.
        So it will fetch data and write file to resources folder.

        :Keyword Arguments:
        * *name* (``str``) --
            Resource name.
        * *path* (``str``) --
            Data where we can find the resource file
            (it could be an URL or a filepath).
        * *download* (``boolean``) --
            A boolean that tell if the data will be downloaded
            in the resources folder.
        """
        store = StoreImpl()
        store.add_resource(**kwargs)

    def delete_resource(self, **kwargs):
        store = StoreImpl()
        store.remove_resource(**kwargs)

    def get_resources(self):
        store = StoreImpl()
        return store.get_resources()

    def check(self) -> bool:
        path = os.path.join(
            os.path.abspath(self.repo_directory), "manifest.json"
        )
        data = manifest.read_manifest(path)
        return manifest.check_manifest(data)

    def fetch(self, remote_name: str):
        r"""
        Update all references of a remote.
        Equivalent of git fetch.

        :param remote_name:
        Name of the remote.
        :type remote_name: ``str``
        """
        if remote_name is not None:
            if not isinstance(remote_name, str):
                raise DeltaTypeError("Wrong type for remote_name. Need a str.")
        with DeltaGitHandler() as repo:
            repo.load_local_repo(self.repo_directory)
            repo.fetch(remote_name)

    def sync(self):
        manifest_path = os.path.join(
            os.path.abspath(self.repo_directory), "manifest.json"
        )
        _manifest = manifest.read_manifest(manifest_path)
        if "resources" in _manifest:
            for item in _manifest["resources"]["items"]:
                self.add_resource(
                    name=item["name"], path=item["source_url"], download=True
                )

    @staticmethod
    def execute_git_command(*args, **kwargs):
        """
        Execute a git command.

        Available kwargs :
        * *path* (``str`` or ``None``) --
            Corresponds to the repository path.

        :return (str(stdout | stderr), (int(status)))

        Examples :
        * execute_git_command("commit", "-m", "this is a commit")
        * execute_git_command("log", path="repository_path")
        * execute_git_command("status")
        """
        path = kwargs.get("path", None)
        if not isinstance(path, (str, type(None))):
            raise TypeError("Error : path must be None or a str")
        status, out, err = Git(path).execute(
            ["git", *args],
            with_exceptions=False,
            with_extended_output=True,
            stdout_as_string=True,
        )
        res = err if (status != 0) else out
        return res, status

    @staticmethod
    def get_runner_factory(kind: str) -> Callable[[Model], JobBuilder]:
        if kind == "python":
            return PythonRunner
        raise ValueError(f"Unknown runner kind '{kind}'")

    @staticmethod
    def generate_docker_build_context(
        path: str, dockerfile_content: str
    ) -> str:
        with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as ctx:
            with tempfile.NamedTemporaryFile() as dockerfile:
                dockerfile.write(dockerfile_content.encode(encoding="utf-8"))
                dockerfile.flush()
                with tarfile.open(ctx.name, "w") as tar:
                    tar.add(path, arcname=".")
                    tar.add(
                        dockerfile.name, arcname="Dockerfile", recursive=False
                    )
            return ctx.name

    def docker_build(
        self,
        version: str = "dev",
        registry: str = None,
        no_cache: bool = False,
    ):
        manifest_json = parse(
            os.path.join(self._repo_directory, "manifest.json")
        )
        if not manifest_json.models:
            logging.info(f"No models images to build")
            return
        for name, model in manifest_json.models.items():
            logging.info(f"Building image for '{name}' model.")
            # retrieve runner
            runner = self.get_runner_factory(model.type)(model)
            # generate dockerfile via the runner
            dockerfile_str = runner.generate_dockerfile()
            # generate docker build context
            context = self.generate_docker_build_context(
                os.path.join(self._repo_directory, model.path), dockerfile_str
            )
            # perform docker build
            try:
                with open(context, "rb") as ctx:
                    tag = f"{manifest_json.name}/{name}:{version}"
                    if registry is not None:
                        tag = f"{registry}/{tag}"
                    cli = docker.from_env()
                    cli.images.build(
                        custom_context=True,
                        rm=True,
                        fileobj=ctx,
                        tag=tag,
                        platform="linux/amd64",
                        nocache=no_cache,
                    )
                    logging.info(f"'{name}' model image successfully built.")
            except docker.errors.DockerException as ex:
                logging.error("Error during docker build")
                raise ex
            finally:
                # remove docker build
                os.remove(context)
