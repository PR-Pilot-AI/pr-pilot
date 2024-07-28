import logging
from pathlib import Path
from typing import List

import git
import yaml
from django.conf import settings
from github.Repository import Repository
from langchain_core.tools import StructuredTool
from pydantic import Field, BaseModel, ValidationError
from yaml.scanner import ScannerError

from engine.agents.behavior import AgentBehavior
from engine.file_system import FileSystem
from engine.models.task_event import TaskEvent
from engine.models.task import Task

logger = logging.getLogger(__name__)


class Project(BaseModel):
    name: str = Field(description="Name of the project")
    main_branch: str = Field(description="Name of the main branch")

    def caching_enabled(self):
        """Determine if caching is enabled for the repository."""
        task = Task.current()
        gh = task.github
        repo: Repository = gh.get_repo(self.name)
        # Caching is enabled if the repository is public
        return not repo.private

    def is_active_open_source_project(self):
        task = Task.current()
        gh = task.github
        repo: Repository = gh.get_repo(self.name)
        num_contributors = repo.get_contributors().totalCount
        participation = repo.get_stats_participation()
        commits_last_four_weeks = sum(participation.all[-4:])
        is_open_source = (
            repo.private is False and repo.license in settings.OSI_APPROVED_LICENSES
        )
        eligible = (
            num_contributors > settings.OPEN_SOURCE_CONTRIBUTOR_THRESHOLD
            and commits_last_four_weeks > settings.OPEN_SOURCE_COMMITS_THRESHOLD
            and is_open_source
        )
        logger.info(
            f"{self.name} eligible for open source project: {eligible} ("
            f"{num_contributors} contributors, "
            f"{commits_last_four_weeks} commits, public={not repo.private}, license={repo.license})"
        )
        return eligible

    @staticmethod
    def commit_all_changes(message, push=False):
        repo = git.Repo(settings.REPO_DIR)
        repo.git.add(A=True)
        commit = repo.index.commit(message)
        TaskEvent.add(
            actor="assistant",
            action="commit_changes",
            message=message,
            target=commit.hexsha,
        )
        if push:
            origin = repo.remote(name="origin")
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

    def load_pilot_hints(self):
        """Load pilot hints from the repository"""
        file_system = FileSystem()
        node = file_system.get_node(Path(".pilot-hints.md"))
        return node.content if node else ""

    def load_pilot_behaviors(self, task, project_info) -> List[StructuredTool]:
        """Load agent behaviors from the repository"""
        file_system = FileSystem()
        node = file_system.get_node(Path(".pilot-behaviors.yaml"))
        if node:
            try:
                behaviors = yaml.safe_load(node.content)
                tools = [
                    AgentBehavior(**behavior).to_agent_tool(
                        task, project_info, self.load_pilot_hints()
                    )
                    for behavior in behaviors
                ]
            except ScannerError:
                raise ValueError("Invalid YAML in .pilot-behaviors.yaml")
            except ValidationError as e:
                raise ValueError(
                    f"Invalid agent behavior in .pilot-behaviors.yaml: {e}"
                )

            logger.info(f"Loaded {len(tools)} agent behaviors from {self.name}")
            return tools
        else:
            logger.info("No agent behaviors found")
        return []

    def discard_all_changes(self):
        logger.info("Discarding all changes")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.reset(hard=True)

    def fetch_remote(self):
        repo = git.Repo(settings.REPO_DIR)
        origin = repo.remote(name="origin")
        origin.fetch()

    def checkout_latest_default_branch(self):
        logger.info(f"Checking out latest {self.main_branch} branch")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.checkout(self.main_branch)

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
        repo.git.checkout("-b", branch_name)

    def push_branch(self, branch):
        logger.info(f"Pushing branch {branch} to origin")
        repo = git.Repo(settings.REPO_DIR)
        origin = repo.remote(name="origin")
        origin.push(
            refspec="{}:refs/heads/{}".format(branch, branch), set_upstream=True
        )

    def delete_branch(self, branch):
        logger.info(f"Deleting branch {branch}")
        repo = git.Repo(settings.REPO_DIR)
        repo.git.branch("-d", branch)

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
        task = Task.current()
        g = task.github
        # Get the repository where you want to create the pull request
        repo = g.get_repo(task.github_project)
        logger.info(f"Creating pull request from {head} to {self.main_branch}")
        labels.append("pr-pilot")
        if task.issue_number:
            issue = repo.get_issue(task.issue_number)
            body += f"\n**Origin:** [{issue.title}]({task.comment_url})"
        pr = repo.create_pull(title=title, body=body, head=head, base=self.main_branch)
        pr.set_labels(*labels)
        TaskEvent.add(
            actor="assistant",
            action="create_pull_request",
            target=pr.number,
            message=f"Create [PR #{pr.number}]({pr.html_url}) for branch `{head}`",
        )
        return pr
