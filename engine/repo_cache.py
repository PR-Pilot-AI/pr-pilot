import logging
import os.path
import shutil
import subprocess

import git
from django.conf import settings


logger = logging.getLogger(__name__)


class RepoCache:

    def __init__(
        self, github_repo: str, github_token: str, workspace=settings.REPO_DIR
    ):
        self.repo = github_repo
        self.token = github_token
        self.workspace = workspace
        owner, repo = self.repo.split("/")
        self.cache_destination = str(os.path.join(settings.REPO_CACHE_DIR, owner, repo))
        self.git_repo_url = f"https://x-access-token:{self.token}@github.com/{self.repo}.git"

    def is_cloned(self):
        """Check if the repository is cloned in the cache."""
        return (
            os.path.exists(self.cache_destination)
            and not git.Repo(self.cache_destination).bare
        )

    def copy_to_workspace(self):
        """Copy the repository to the workspace."""
        logger.info(f"Copying {self.cache_destination} to {self.workspace}")
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace)
        shutil.copytree(self.cache_destination, self.workspace)
        subprocess.run(["git", "remote", "set-url", "origin", self.git_repo_url], check=True, cwd=self.workspace)

    def clone(self, destination: str):
        """Clone the repository."""
        git.Repo.clone_from(self.git_repo_url, destination)
        logger.info(f"Cloned repo {self.repo} to {destination}")

    def setup_workspace(self):
        """Copy the repository to the workspace and pull the latest changes."""
        # If caching is enabled, clone the repository to the cache directory
        if not self.is_cloned():
            self.clone(self.cache_destination)
        logger.info(
            f"Pulling latest changes for {self.repo} in {self.cache_destination}"
        )
        repo = git.Repo(self.cache_destination)
        origin = repo.remote(name="origin")
        origin.fetch()
        origin.pull()
        self.copy_to_workspace()
