import logging

import git
from django.conf import settings
from pydantic import Field, BaseModel

from engine.models import Task, TaskEvent

logger = logging.getLogger(__name__)


class Project(BaseModel):
    name: str = Field(description="Name of the project")
    main_branch: str = Field(description="Name of the main branch")

    @staticmethod
    def commit_all_changes(message, push=False):
        repo = git.Repo(settings.REPO_DIR)
        repo.git.add(A=True)

        repo.index.commit(message, no_verify=True)
        if push:
            origin = repo.remote(name='origin')
            origin.push(repo.active_branch.name, set_upstream=True)

    @staticmethod
    def commit_changes_of_file(file_path, message):
        repo = git.Repo(settings.REPO_DIR)
        repo.git.add(file_path)
        repo.index.commit(message)

    @staticmethod
    def from_github():
        task = Task.current()
        gh = task.github
        repo = gh.get_repo(task.github_project)
        return Project(name=repo.full_name, main_branch=repo.default_branch)

    def discard_all_changes(self):
        logger.info("Discarding all changes")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.reset(hard=True)

    def fetch_remote(self):
        repo = git.Repo(settings.REPO_DIR)
        origin = repo.remote(name='origin')
        origin.fetch()

    def checkout_latest_default_branch(self):
        logger.info(f"Checking out latest {self.main_branch} branch")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.checkout(self.main_branch)
        repo.git.pull()

    def checkout_branch(self, branch):
        logger.info(f"Checking out branch {branch}")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.checkout(branch)

    def has_uncommitted_changes(self):
        repo = git.Repo(settings.REPO_DIR)
        return repo.is_dirty(untracked_files=True)

    def create_new_branch(self, branch_name):
        logger.info(f"Creating new branch {branch_name}")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.checkout('-b', branch_name)

    def push_branch(self, branch):
        logger.info(f"Pushing branch {branch} to origin")
        repo = git.Repo(settings.REPO_DIR)
        origin = repo.remote(name='origin')
        origin.push(refspec='{}:refs/heads/{}'.format(branch, branch), set_upstream=True)

    def delete_branch(self, branch):
        logger.info(f"Deleting branch {branch}")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.branch('-d', branch)

    def get_diff_to_main(self):
        repo = git.Repo(settings.REPO_DIR)
        diff = repo.git.diff(f"{self.main_branch}...{repo.active_branch.name}")
        return diff.strip()

    @property
    def active_branch(self):
        return git.Repo(settings.REPO_DIR).active_branch.name

    def create_pull_request(self, title, body, head, labels=[]):
        if not head:
            head = self.active_branch
        g = Task.current().github
        # Get the repository where you want to create the pull request
        repo = g.get_repo(Task.current().github_project)
        logger.info(f"Creating pull request from {head} to {self.main_branch}")
        labels.append("pr-pilot")
        pr = repo.create_pull(title=title, body=body, head=head, base=self.main_branch)
        pr.set_labels(*labels)
        TaskEvent.add(actor="assistant", action="create_pull_request", target=head,
                      message=f"Created [PR {pr.number}]({pr.html_url}) for branch `{head}`")
        return pr

