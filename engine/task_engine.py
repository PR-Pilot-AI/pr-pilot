import base64
import logging
import os
import shutil
import threading
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from git import Repo
from github import Github
from github.PullRequest import PullRequest

from accounts.models import UserBudget, PilotUser
from engine.agents.integration_tools import integration_tools_for_user
from engine.agents.pr_pilot_agent import create_pr_pilot_agent
from engine.channels import broadcast
from engine.langchain.generate_pr_info import generate_pr_info, LabelsAndTitle
from engine.langchain.generate_task_title import generate_task_title
from engine.models.cost_item import CostItem
from engine.models.task import Task, TaskType
from engine.models.task_bill import TaskBill
from engine.models.task_event import TaskEvent
from engine.project import Project
from engine.repo_cache import RepoCache
from engine.util import slugify
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)

MAX_BRANCH_NAME_LENGTH = 24


class TaskEngine:

    def __init__(self, task: Task, max_steps=5):
        os.environ["GIT_COMMIT_HOOK"] = ""
        self.task = task
        self.max_steps = max_steps
        self.executor = create_pr_pilot_agent(
            task.gpt_model,
            image_support=self.task.image is not None,
            additional_tools=integration_tools_for_user(
                PilotUser.objects.get(username=task.github_user)
            ),
        )
        self.github_token = get_installation_access_token(self.task.installation_id)
        self.github = Github(self.github_token)
        self.github_repo = self.github.get_repo(self.task.github_project)
        self.project = Project(
            name=self.github_repo.full_name, main_branch=self.github_repo.default_branch
        )

    def create_unique_branch_name(self, basis: str):
        """Create branch name based on a given string. If branch exists,
        add increasing numbers at the end"""
        slugified_basis = slugify(basis)
        # Cut off branch name at las hyphen before 24 characters
        if "-" in slugified_basis:
            while len(slugified_basis) > MAX_BRANCH_NAME_LENGTH:
                slugified_basis = slugified_basis[: slugified_basis.rindex("-")]

        unique_branch_name = slugified_basis[:24]
        repo = Repo(settings.REPO_DIR)

        counter = 1
        original_branch_name = unique_branch_name

        while unique_branch_name in [
            str(ref).replace("origin/", "") for ref in repo.refs
        ]:
            unique_branch_name = f"{original_branch_name}-{counter}"
            counter += 1
        return unique_branch_name

    def setup_working_branch(self, branch_name_basis: str):
        """
        Create a new branch based on the given branch name basis.
        :param branch_name_basis: String to use for generating the branch name
        :return: Branch name
        """

        self.project.discard_all_changes()
        self.project.checkout_latest_default_branch()
        tool_branch = self.create_unique_branch_name(branch_name_basis)
        logger.info(f"Creating new local branch '{tool_branch}'...")
        self.project.create_new_branch(tool_branch)
        return tool_branch

    def finalize_working_branch(self, branch_name: str) -> bool:
        """
        Finalize the working branch by committing and pushing changes.
        :param branch_name: Name of the working branch
        :return: True if changes were pushed, False if no changes were made
        """
        if self.project.has_uncommitted_changes():
            logger.warning(
                f"Found uncommitted changes on {branch_name!r} branch! Committing..."
            )
            self.project.commit_all_changes(message="Uncommitted changes")
        if self.project.get_diff_to_main():
            logger.info(f"Found changes on {branch_name!r} branch. Pushing changes ...")
            self.project.push_branch(branch_name)
            TaskEvent.add(
                actor="assistant",
                action="push_branch",
                target=branch_name,
                message=f"Push branch `{branch_name}`",
            )
            self.project.checkout_latest_default_branch()
            return True
        else:
            logger.info(f"No changes on {branch_name} branch. Deleting...")
            self.project.checkout_latest_default_branch()
            self.project.delete_branch(branch_name)
            return False

    def generate_task_title(self):
        if self.task.task_type == TaskType.GITHUB_PR_REVIEW_COMMENT:
            pr = self.github_repo.get_pull(self.task.pr_number)
            self.task.title = generate_task_title(pr.body, self.task.user_request)
        elif self.task.task_type == TaskType.GITHUB_ISSUE:
            issue = self.github_repo.get_issue(self.task.issue_number)
            self.task.title = generate_task_title(issue.body, self.task.user_request)
        else:
            self.task.title = generate_task_title("", self.task.user_request)
        self.task.save()
        broadcast(
            str(self.task.id),
            {
                "type": "title_update",
                "data": self.task.title,
            },
        )

    def run(self) -> str:
        self.task.status = "running"
        self.broadcast_status_update("running")
        self.task.save()
        budget = UserBudget.get_user_budget(self.task.github_user)
        if budget.budget < Decimal("0.00"):
            TaskEvent.add(
                actor="assistant",
                action="budget_exceeded",
                target=self.task.github_user,
                message="Budget exceeded. Please add credits to your account.",
            )
            self.task.status = "failed"
            self.task.result = "Budget exceeded. Please add credits to your account."
            self.task.context.respond_to_user(self.task.result)
            self.task.save()
            self.broadcast_status_update("failed", self.task.result)
            return self.task.result
        # Generate task title in the background
        task_title_thread = threading.Thread(target=self.generate_task_title)
        task_title_thread.start()
        self.clone_github_repo()

        try:
            # If task is a PR, checkout the PR branch
            if self.task.pr_number:
                TaskEvent.add(
                    actor="assistant",
                    action="checkout_pr_branch",
                    target=self.task.head,
                    message="Check out PR branch",
                )
                self.project.checkout_branch(self.task.head)
                working_branch = self.task.head
            elif self.task.branch:
                # If task is a standalone task, checkout the branch
                working_branch = self.task.branch
                TaskEvent.add(
                    actor="assistant",
                    action="checkout_branch",
                    target=self.task.branch,
                    message=f"Check out PR branch `{self.task.branch}`",
                )
                self.project.checkout_branch(self.task.branch)
            else:
                # No branch or PR number provided, create a new branch
                # Wait for task title to be generated
                task_title_thread.join()
                working_branch = self.setup_working_branch(self.task.title)
            # Make sure we never work directly on the main branch
            if self.project.active_branch == self.project.main_branch:
                raise ValueError(
                    f"Cannot work on the main branch {self.project.main_branch}."
                )
            project_info = self.github_repo.description
            if self.github_repo.fork:
                project_info += f"\n\nThis project is a fork of [{self.github_repo.parent.full_name}]({self.github_repo.parent.html_url})."
            if self.task.image:
                image_base64 = base64.b64encode(self.task.image).decode()
            else:
                image_base64 = ""
            date_and_time = (
                timezone.now().isoformat() + " " + str(timezone.get_current_timezone())
            )
            executor_result = self.executor.invoke(
                {
                    "encoded_image_url": f"data:image/png;base64,{image_base64}",
                    "user_request": self.task.user_request,
                    "github_project": self.task.github_project,
                    "project_info": project_info,
                    "pilot_hints": self.project.load_pilot_hints(),
                    "current_time": date_and_time,
                }
            )
            self.task.result = executor_result["output"]
            self.task.status = "completed"
            final_response = executor_result["output"]
            if working_branch and self.task.pr_number:
                # We are working on an existing PR
                if self.project.get_diff_to_main():
                    logger.info(
                        f"Found changes on {working_branch!r} branch. Pushing ..."
                    )
                    self.project.push_branch(working_branch)
            elif working_branch and self.finalize_working_branch(working_branch):
                # Do not create a PR if user asked us to work on their branch
                if not self.task.branch:
                    logger.info(f"Creating pull request for branch {working_branch}")
                    pr_info = generate_pr_info(final_response)
                    if not pr_info:
                        pr_info = LabelsAndTitle(
                            title=self.task.title, labels=["pr-pilot"]
                        )
                    pr: PullRequest = Project.from_github().create_pull_request(
                        title=pr_info.title,
                        body=final_response,
                        head=working_branch,
                        labels=pr_info.labels,
                    )
                    final_response += (
                        f"\n\n**PR**: [{pr.title}]({pr.html_url})\n\nIf you require further changes, "
                        f"continue our conversation over there!"
                    )
                    self.task.pr_number = pr.number
                    self.task.branch = working_branch
            final_response += f"\n\n---\n📋 **[Log](https://app.pr-pilot.ai/dashboard/tasks/{str(self.task.id)}/)**"
            final_response += f" ↩️ **[Undo](https://app.pr-pilot.ai/dashboard/tasks/{str(self.task.id)}/undo/)**"
            self.broadcast_status_update("completed", self.task.result)
        except Exception as e:
            self.task.status = "failed"
            self.broadcast_status_update("failed")
            self.task.result = str(e)
            logger.error("Failed to run task", exc_info=e)
            dashboard_link = f"[Your Dashboard](https://app.pr-pilot.ai/dashboard/tasks/{str(self.task.id)}/)"
            final_response = f"I'm sorry, something went wrong, please check {dashboard_link} for details."
        finally:
            self.task.save()
        self.task.context.respond_to_user(final_response.strip().replace("/pilot", ""))
        self.create_bill()
        return final_response

    def create_bill(self):
        is_open_source = self.project.is_active_open_source_project()
        if is_open_source:
            discount = settings.OPEN_SOURCE_CONTRIBUTOR_DISCOUNT_PERCENT
        else:
            discount = 0.0
        bill = TaskBill(
            task=self.task,
            discount_percent=discount,
            project_is_open_source=is_open_source,
            total_credits_used=sum(
                [c.credits for c in CostItem.objects.filter(task=self.task)]
            ),
            user_is_owner=self.github_repo.owner.name == self.task.github_user,
        )
        bill.save()
        logger.info(f"Discount applied: {discount}%")
        logger.info(f"Total cost: {bill.final_cost} credits")
        budget = UserBudget.get_user_budget(self.task.github_user)
        budget.budget = budget.budget - Decimal(str(bill.final_cost))
        logger.info(
            f"Remaining budget for user {self.task.github_user}: {budget.budget} credits"
        )
        budget.save()

    def clone_github_repo(self):

        if os.path.exists(settings.REPO_DIR):
            logger.info("Deleting existing directory contents.")
            shutil.rmtree(settings.REPO_DIR)
        cache = RepoCache(self.task.github_project, self.github_token)
        github_repo_url = f"https://github.com/{self.task.github_project}"
        if self.project.caching_enabled():
            logger.info("Caching is enabled! Setting up workspace...")
            TaskEvent.add(
                actor="assistant",
                action="clone_repo",
                target=self.task.github_project,
                message=f"Load cached repository [{self.task.github_project}]({github_repo_url})",
            )
            cache.setup_workspace()
        else:
            # If caching is disabled, clone it directly into the workspace
            logger.info("Caching is disabled! Cloning directly into workspace...")
            TaskEvent.add(
                actor="assistant",
                action="clone_repo",
                target=self.task.github_project,
                message=f"Clone repository [{self.task.github_project}]({github_repo_url})",
            )
            cache.clone(settings.REPO_DIR)

    def broadcast_status_update(self, new_status: str, message: str = None):
        """Broadcast a status update to the task's websocket channel."""
        broadcast(
            str(self.task.id),
            {
                "type": "status_update",
                "data": {
                    "status": new_status,
                    "message": message,
                },
            },
        )
