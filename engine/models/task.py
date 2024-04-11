import logging
import os
import threading
import uuid
from enum import Enum
from functools import lru_cache

from django.conf import settings
from django.db import models
from github import Github, GithubException

from accounts.models import UserBudget
from engine.job import KubernetesJob
from engine.task_context.github_issue import GithubIssueContext
from engine.task_context.pr_review_comment import PRReviewCommentContext
from engine.task_context.task_context import TaskContext
from engine.util import run_task_in_background
from webhooks.jwt_tools import get_installation_access_token


logger = logging.getLogger(__name__)


class TaskType(Enum):
    GITHUB_ISSUE = "github_issue"
    GITHUB_PR_REVIEW_COMMENT = "github_review_comment"
    STANDALONE = "standalone"


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(max_length=200, choices=[(tag, tag.value) for tag in TaskType], default=TaskType.STANDALONE.value)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    installation_id = models.IntegerField()
    github_project = models.CharField(max_length=200)
    github_user = models.CharField(max_length=200)
    branch = models.CharField(max_length=200)
    issue_number = models.IntegerField(blank=True, null=True)
    pr_number = models.IntegerField(blank=True, null=True)
    user_request = models.TextField(blank=True)
    head = models.CharField(max_length=200, blank=True, null=True)
    base = models.CharField(max_length=200, blank=True, null=True)
    comment_id = models.IntegerField()
    comment_url = models.CharField(max_length=200, blank=True, null=True)
    response_comment_id = models.IntegerField(blank=True, null=True)
    response_comment_url = models.CharField(max_length=200, blank=True, null=True)
    result = models.TextField(blank=True)
    pilot_command = models.TextField(blank=True)

    def __str__(self):
        return self.title

    @property
    @lru_cache()
    def context(self) -> TaskContext:
        if self.task_type == TaskType.GITHUB_ISSUE.value:
            return GithubIssueContext(self)
        elif self.task_type == TaskType.GITHUB_PR_REVIEW_COMMENT.value:
            return PRReviewCommentContext(self)
        elif self.task_type == TaskType.STANDALONE.value:
            return TaskContext(self)
        else:
            raise ValueError(f"Invalid task type: {self.task_type}")

    @staticmethod
    @lru_cache()
    def current() -> 'Task':
        if not settings.TASK_ID:
            raise ValueError("TASK_ID is not set")
        return Task.objects.get(id=settings.TASK_ID)

    @property
    @lru_cache()
    def github(self) -> Github:
        return Github(get_installation_access_token(self.installation_id))

    @property
    def reversible_events(self):
        return [event for event in self.events.filter(reversed=False) if event.reversible]

    @property
    def request_issue(self):
        repo = self.github.get_repo(self.github_project)
        if self.pr_number:
            return repo.get_pull(self.pr_number)
        else:
            return repo.get_issue(self.issue_number)

    @property
    def request_comment(self):
        if self.pr_number:
            try:
                return self.request_issue.get_review_comment(self.comment_id)
            except GithubException as e:
                if e.status == 404:
                    return self.request_issue.get_issue_comment(self.comment_id)
                else:
                    raise
        else:
            return self.request_issue.get_comment(self.comment_id)

    @property
    def response_comment(self):
        repo = self.github.get_repo(self.github_project)
        if self.pr_number:
            pr = repo.get_pull(self.pr_number)
            try:
                return pr.get_review_comment(self.response_comment_id)
            except GithubException as e:
                if e.status == 404:
                    return pr.get_issue_comment(self.response_comment_id)
                else:
                    raise
        else:
            issue = repo.get_issue(self.issue_number)
            return issue.get_comment(self.response_comment_id)

    def create_response_comment(self, message):
        repo = self.github.get_repo(self.github_project)
        if self.pr_number:
            pr = repo.get_pull(self.pr_number)
            try:
                comment = pr.create_review_comment_reply(self.comment_id, message)
            except GithubException as e:
                if e.status == 404:
                    comment = pr.create_issue_comment(message)
                else:
                    raise
        else:
            issue = repo.get_issue(self.issue_number)
            comment = issue.create_comment(message)
        self.response_comment_id = comment.id
        self.response_comment_url = comment.html_url
        self.save()
        return comment

    def user_budget_empty(self):
        budget = UserBudget.get_user_budget(self.github_user)
        return budget.budget <= 0

    def schedule(self):
        self.context.acknowledge_user_prompt()
        if self.user_budget_empty():
            logger.info(f'User {self.github_user} has no budget')
            self.context.respond_to_user(
                "You have used up your budget. Please visit the [Dashboard](https://app.pr-pilot.ai) to purchase more credits.")
            self.status = "failed"
            self.save()
            return

        if not self.user_can_write():
            message = f"Sorry @{self.github_user}, you must be a collaborator of `{self.github_project}` to run commands on this project."
            self.context.respond_to_user(message)
            self.status = "failed"
            self.save()
            return

        if settings.JOB_STRATEGY == 'thread':
            # In local development, just run the task in a background thread
            settings.TASK_ID = self.id
            os.environ["TASK_ID"] = str(self.id)
            logger.info(f"Running task in debug mode: {self.id}")
            thread = threading.Thread(target=run_task_in_background, args=(self.id,))
            thread.start()
        elif settings.JOB_STRATEGY == 'kubernetes':
            # In production, run the task in a Kubernetes job
            job = KubernetesJob(self)
            job.spawn()
        elif settings.JOB_STRATEGY == 'log':
            # In testing, just log the task
            logger.info(f"Running task in log mode: {self.id}")
        else:
            raise ValueError(f"Invalid JOB_STRATEGY: {settings.JOB_STRATEGY}")
        self.status = "scheduled"
        self.save()

    def user_can_write(self) -> bool:
        """Check if the user has write access to the repository"""
        repo = self.github.get_repo(self.github_project)
        permission = repo.get_collaborator_permission(self.github_user)
        return permission == 'write' or permission == 'admin'
