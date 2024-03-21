import logging
import os
import threading
import uuid
from functools import lru_cache

from django.conf import settings
from django.core.management import call_command
from django.db import models
from github import Github, GithubException

from engine.job import KubernetesJob
from engine.util import run_task_in_background
from webhooks.jwt_tools import get_installation_access_token

logger = logging.getLogger(__name__)


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    def __str__(self):
        return self.title

    @staticmethod
    @lru_cache()
    def current():
        if not settings.TASK_ID:
            raise ValueError("TASK_ID is not set")
        return Task.objects.get(id=settings.TASK_ID)

    @property
    def github(self) -> Github:
        return Github(get_installation_access_token(self.installation_id))

    @property
    def reversible_events(self):
        return [event for event in self.events.filter(reversed=False) if event.reversible]

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

    @staticmethod
    def schedule(**kwargs):
        new_task = Task(**kwargs, status="scheduled")
        repo = new_task.github.get_repo(new_task.github_project)

        if not new_task.user_can_write():
            message = f"Sorry @{new_task.github_user}, you must be a collaborator of `{new_task.github_project}` to run commands on this project."
            if new_task.pr_number:
                pr = repo.get_pull(new_task.pr_number)
                try:
                    comment = pr.create_review_comment_reply(new_task.comment_id, message)
                except GithubException as e:
                    if e.status == 404:
                        comment = pr.create_issue_comment(message)
                    else:
                        raise
            else:
                issue = repo.get_issue(new_task.issue_number)
                comment = issue.create_comment(message)
            new_task.status = "failed"
            new_task.result = message
            new_task.response_comment_id = comment.id
            new_task.response_comment_url = comment.html_url
            new_task.save()
            return new_task
        initial_response = f"⌛ I'm on it! Track my progress in the [Dashboard](https://app.pr-pilot.ai/dashboard/tasks/{str(new_task.id)}/). I'll update this comment when I'm done..."
        new_task.create_response_comment(initial_response)
        new_task.save()
        if settings.DEBUG:
            settings.TASK_ID = new_task.id
            os.environ["TASK_ID"] = str(new_task.id)
            logger.info(f"Running task in debug mode: {new_task.id}")
            thread = threading.Thread(target=run_task_in_background, args=(new_task.id,))
            thread.start()
        else:
            job = KubernetesJob(new_task)
            job.spawn()
        return new_task

    def user_can_write(self) -> bool:
        repo = self.github.get_repo(self.github_project)
        permission = repo.get_collaborator_permission(self.github_user)
        return permission == 'write' or permission == 'admin'


class TaskEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="events")
    timestamp = models.DateTimeField(auto_now_add=True)
    reversed = models.BooleanField(default=False)
    actor = models.CharField(max_length=200)
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)


    def undo(self):
        if self.action == "create_github_issue":
            logger.info(f"Closing issue {self.target}")
            self.task.github.get_repo(self.task.github_project).get_issue(int(self.target)).edit(state="closed")
            TaskEvent.add(actor="assistant", action="close_github_issue", target=self.target, message="Closed github issue", task_id=self.task.id)
            self.reversed = True
            self.save()
        elif self.action == "create_pull_request":
            logger.info(f"Closing pull request {self.target}")
            self.task.github.get_repo(self.task.github_project).get_pull(int(self.target)).edit(state="closed")
            TaskEvent.add(actor="assistant", action="close_pull_request", target=self.target, message="Closed pull request", task_id=self.task.id)
            self.reversed = True
            self.save()
        elif self.action == "comment_on_issue":
            logger.info(f"Deleting comment {self.target}")
            if self.task.pr_number:
                pr = self.task.github.get_repo(self.task.github_project).get_pull(self.task.pr_number)
                pr.get_issue_comment(int(self.target)).delete()
            else:
                issue = self.task.github.get_repo(self.task.github_project).get_issue(self.task.issue_number)
                issue.get_comment(int(self.target)).delete()
            TaskEvent.add(actor="assistant", action="delete_github_comment", target=self.target, message="Deleted github comment", task_id=self.task.id)
            self.reversed = True
            self.save()

    @property
    def reversible(self):
        reversible_actions = ["create_github_issue", "create_pull_request", "comment_on_issue"]
        return self.action in reversible_actions

    @staticmethod
    def add(actor: str, action: str, target: str = None, message="", task_id=None, transaction=None, changes=[]):
        if not task_id:
            task_id = settings.TASK_ID
        if not task_id:
            raise ValueError("No task ID was provided. Please set TASK_ID in the environment or pass it as an argument.")
        new_entry = TaskEvent(actor=actor, action=action, target=target, message=message, task_id=task_id)
        new_entry.save()
        return new_entry


class CostItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    model_name = models.CharField(max_length=200)
    prompt_token_count = models.IntegerField()
    completion_token_count = models.IntegerField()
    requests = models.IntegerField()
    total_cost_usd = models.FloatField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="cost_items", null=True)

    @property
    def credits(self):
        return self.total_cost_usd * float(settings.CREDIT_MULTIPLIER) * float(100)

    def __str__(self):
        return f"{self.title} - ${self.total_cost_usd}"

