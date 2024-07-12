import logging
import uuid
from datetime import timedelta
from enum import Enum
from functools import lru_cache

from django.conf import settings
from django.db import models
from django.utils import timezone
from github import Github, GithubException

from engine.task_context.github_issue import GithubIssueContext
from engine.task_context.pr_review_comment import PRReviewCommentContext
from engine.task_context.task_context import TaskContext
from engine.task_scheduler import TaskScheduler
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)


class TaskType(Enum):
    GITHUB_ISSUE = "github_issue"
    GITHUB_PR_REVIEW_COMMENT = "github_review_comment"
    STANDALONE = "standalone"


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(
        max_length=200,
        choices=[(tag, tag.value) for tag in TaskType],
        default=TaskType.STANDALONE.value,
    )
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    installation_id = models.BigIntegerField()
    github_project = models.CharField(max_length=200)
    github_user = models.CharField(max_length=200)
    branch = models.CharField(max_length=200)
    issue_number = models.IntegerField(blank=True, null=True)
    pr_number = models.IntegerField(blank=True, null=True)
    user_request = models.TextField(blank=True)
    head = models.CharField(max_length=200, blank=True, null=True)
    base = models.CharField(max_length=200, blank=True, null=True)
    comment_id = models.BigIntegerField(null=True)
    comment_url = models.CharField(max_length=200, blank=True, null=True)
    response_comment_id = models.BigIntegerField(blank=True, null=True)
    response_comment_url = models.CharField(max_length=200, blank=True, null=True)
    result = models.TextField(blank=True)
    pilot_command = models.TextField(blank=True)
    gpt_model = models.CharField(
        max_length=200, blank=True, null=True, default="gpt-4o"
    )
    image = models.BinaryField(
        blank=True, null=True, help_text="An image to be used in the task"
    )

    def __str__(self):
        return self.title

    def would_reach_rate_limit(self):
        """Determine if scheduling the task would hit the rate limit for the project."""
        tasks_created_in_last_10_minutes = Task.objects.filter(
            github_project=self.github_project,
            created__gte=timezone.now()
            - timedelta(minutes=settings.TASK_RATE_LIMIT_WINDOW),
        )
        return tasks_created_in_last_10_minutes.count() >= settings.TASK_RATE_LIMIT

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
    def current() -> "Task":
        if not settings.TASK_ID:
            raise ValueError("TASK_ID is not set")
        return Task.get(settings.TASK_ID)

    @staticmethod
    @lru_cache()
    def get(task_id: str) -> "Task":
        if not settings.TASK_ID:
            raise ValueError("TASK_ID is not set")
        return Task.objects.get(id=task_id)

    @property
    @lru_cache()
    def github(self) -> Github:
        return Github(get_installation_access_token(self.installation_id))

    @property
    def reversible_events(self):
        return [
            event for event in self.events.filter(reversed=False) if event.reversible
        ]

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

    def schedule(self):
        scheduler = TaskScheduler(self)
        return scheduler.schedule()
