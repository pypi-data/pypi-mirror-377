from git import Repo
from typing import Any
from urllib.parse import urlparse
from delta.manifest import manifest
import os
import re
import shutil
import logging

TEMPLATE_DIR = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            'template')

FILES_TO_ADD = ['.delta',
                'artifacts',
                'models',
                'resources',
                'sources',
                '.gitignore',
                'manifest.json']

logger = logging.getLogger('Delta')


class DeltaException(Exception):
    pass


def url_validator(url):
    ssh_pattern = (r"(ssh:\/\/)?(?:[a-z_][a-z0-9_]{0,30})@"
                   r"((?:[a-z0-9-_]+\.)+[a-z0-9]+)(?::([0-9]{0,5}))?"
                   r"(\/[^\0\n]+)?")
    return urlparse(url).scheme == 'https' or bool(re.match(ssh_pattern, url))


def get_repo_name_from_url(path):
    return path.split('.git')[0].split('/')[-1]


class DeltaGitHandler:

    def __init__(self):
        self._repo = None
        self._initialize_flag = False
        self._path = None

    def create(self, path_to_save: str):
        try:
            _path = os.path.abspath(path_to_save)
            shutil.copytree(TEMPLATE_DIR, _path)
            manifest.write_manifest(os.path.join(_path, 'manifest.json'))
            _repo = Repo.init(_path)
            if self._initialize_flag:
                self.close()
            self._repo = _repo
            self._path = _path
            self._initialize_flag = True
            self.add(FILES_TO_ADD, force=True)
            self.commit('Initialize Twin')
            logger.info(f"Twin has been initialized at {_path}")
        except Exception:
            raise DeltaException("Error when creating the repo")

    def set_config(self, username, email):
        try:
            self._repo.config_writer().set_value("user",
                                                 "name",
                                                 username).release()
            self._repo.config_writer().set_value("user",
                                                 "email",
                                                 email).release()
            logger.info(f"Config :\n\tusername = {username}\n\t{email}")
        except Exception:
            raise DeltaException("Error when setting config")

    def load_local_repo(self, path: str):
        try:
            _path = os.path.abspath(path)
            _repo = Repo(_path)
            if self._initialize_flag:
                self.close()
            self._repo = _repo
            self._path = _path
            self._initialize_flag = True
            logger.debug(f"Repo {path} has been loaded")
        except Exception:
            raise DeltaException("Error when loading existing repo...")

    def clone(self, path_from: str, path_to_save: str):
        try:
            if not url_validator(path_from):
                raise DeltaException(f'Wrong URL : {path_from}... Verify it.')
            else:
                path_with_repo_name = os.path.join(
                                                path_to_save,
                                                get_repo_name_from_url(
                                                    path_from
                                                )
                                            )
                _repo = Repo.clone_from(path_from, path_with_repo_name)
                _path = os.path.abspath(path_with_repo_name)
                logger.info(f"Repo {path_from} has been cloned "
                            f"and store at {_path}")
                if self._initialize_flag:
                    self.close()
                self._repo = _repo
                self._path = _path
                self._initialize_flag = True
        except Exception:
            raise DeltaException("Error when cloning project. \n"
                                 f"Maybe the path {path_from} doesn't exist. "
                                 "Or check the path where you want to save "
                                 "the repo.")

    def commit(self, message: str):
        if self._initialize_flag:
            try:
                commit = self._repo.index.commit(message)
                logger.info(f"New commit : {commit.name_rev}")
            except Exception:
                raise DeltaException("Error when commiting.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to commit.")

    def add(self, files_to_add: list, force: bool = False):
        if self._initialize_flag:
            try:
                files = []
                if force:
                    files = files_to_add
                else:
                    files = filter(
                        lambda files: not files.startswith('resources/'),
                        files_to_add)
                res = self._repo.index.add(files)
                logger.debug(f"{files_to_add} has been added")
                return res
            except Exception:
                raise DeltaException("Error when adding files "
                                     f"{files_to_add}.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to add files.")

    def pull(self, remote_name: str):
        if self._initialize_flag:
            try:
                remote = None
                if remote_name == '' or remote_name is None:
                    remote = self._repo.remotes.origin
                else:
                    remote = self._repo.remote(name=remote_name)
                if remote is not None:
                    remote.pull(refspec=f"{self._repo.active_branch}:"
                                f"{self._repo.active_branch}")
            except Exception:
                raise DeltaException("Error when pulling.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to pull")

    def push(self, remote_name: str = None, ref_name: str = None):
        if self._initialize_flag:
            try:
                if remote_name == '' or remote_name is None:
                    remote = self._repo.remotes.origin
                else:
                    remote = self._repo.remote(name=remote_name)

                if ref_name == '' or ref_name is None:
                    ref_to_push = self._repo.active_branch
                else:
                    ref_to_push = ref_name
                remote.push(
                            refspec=f"{ref_to_push}:"
                            f"{ref_to_push}"
                        )
                logger.info("Pushed on remote branch "
                            f"{remote_name}/{ref_to_push}")
            except Exception:
                try:
                    logger.warning("Will try with --set-upstream...")
                    self._repo.git.push('--set-upstream',
                                        remote.name,
                                        ref_to_push)
                except Exception:
                    raise DeltaException("Error when trying to push.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to push")

    def fetch(self, remote_name: str):
        if self._initialize_flag:
            try:
                if remote_name == '' or remote_name is None:
                    remote = self._repo.remotes.origin
                else:
                    remote = self._repo.remote(name=remote_name)
                remote.fetch()
            except Exception:
                raise DeltaException("Error when call fetch.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to fetch")

    def create_remote(self, remote_name: str, url: str):
        if self._initialize_flag:
            try:
                self._repo.create_remote(remote_name, url)
                logger.info(f"Remote {remote_name} at {url} "
                            "has been created")
            except Exception:
                raise DeltaException("Error when creating remote.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to create a remote")

    def list_remotes(self):
        if self._initialize_flag:
            try:
                remotes = [remote.name for remote in self._repo.remotes]
                return remotes
            except Exception:
                raise DeltaException("Error when executing command "
                                     "'git remote show'")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to list remotes")

    def status(self):
        if self._initialize_flag:
            try:
                return self._repo.head.reference.log()
            except Exception:
                raise DeltaException("Error when get status.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to get repository status")

    def checkout(self, branch_name: str):
        if self._initialize_flag:
            try:
                self._repo.git.checkout(branch_name)
                logger.info(f"Checkout to branch : {branch_name}")
            except Exception:
                try:
                    self._repo.git.checkout('-b', branch_name)
                    logger.info(f"Checkout to branch : {branch_name}")
                except Exception:
                    raise DeltaException("Error when checkout to "
                                         f"branch {branch_name}. "
                                         "Please verify the name "
                                         "of your branch.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to checkout.")

    def branch(self, branch_name: str):
        if self._initialize_flag:
            try:
                self._repo.git.branch(branch_name)
                logger.info(f"{branch_name} has been created.")
            except Exception:
                raise DeltaException("Error when executing command "
                                     "'git branch <branch name'.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to create a new branch.")

    def remove_branch(self, branch_name: str):
        if self._initialize_flag:
            try:
                self._repo.git.branch('-D', branch_name)
                logger.info(f"{branch_name} has been removed.")
            except Exception:
                raise DeltaException("Error when executing command "
                                     "'git branch -D <branch name'.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to create a new branch.")

    def list_branches(self):
        if self._initialize_flag:
            branches = [branch.name for branch in self._repo.branches]
            remotes = self._repo.remotes
            for remote in remotes:
                for branch_ref in remote.refs:
                    branches.append(branch_ref.name)
            return branches

        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to list all branches.")

    def tag(self, tag_name: str, message: str = ''):
        if self._initialize_flag:
            try:
                res = self._repo.create_tag(tag_name, message=message)
                logger.info(f"New tag {tag_name} has been created")
                return str(res)
            except Exception:
                raise DeltaException("Error when trying to create "
                                     f"new tag {tag_name}.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to tag")

    def list_tag(self) -> list:
        if self._initialize_flag:
            try:
                res = [tag.name for tag in self._repo.tags]
                return res
            except Exception:
                raise DeltaException("Error when trying to listing tags. ")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to list tags")

    def remove_tag(self, tag_name: str):
        if self._initialize_flag:
            try:
                self._repo.git.tag('-d', tag_name)
                logger.info(f"{tag_name} has been removed.")
            except Exception:
                raise DeltaException("Error when trying to remove "
                                     f"tag {tag_name}.")
        else:
            raise DeltaException("Please initialize your repository "
                                 "in order to tag")

    def close(self):
        if self._initialize_flag:
            if self._repo is not None:
                self._repo.close()
                logger.debug("Repo has been closed...")
            self._path = None
            self._initialize_flag = False
            logger.debug("Everything has been closed correctly...")

    def __enter__(self) -> "DeltaGitHandler":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
