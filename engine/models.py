import logging
import os
import threading
import uuid
from functools import lru_cache

from django.conf import settings
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
    pilot_command = models.TextField(blank=True)

    def __str__(self):
        return self.title

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

    def acknowledge_user_prompt(self):
        """Acknowledge the user's prompt so they know we've received their request. This behavior can be overridden
        by subclasses in order to respond in a different way."""
        pass

    def respond_to_user(self, message):
        """
        Respond to the user's request. This behavior can be overridden by subclasses in order to respond in a different way.
        :param message: The message to send to the user
        """
        pass

    def schedule(self):
        self.acknowledge_user_prompt()
        if not self.user_can_write():
            message = f"Sorry @{self.github_user}, you must be a collaborator of `{self.github_project}` to run commands on this project."
            self.respond_to_user(message)
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
                try:
                    pr.get_issue_comment(int(self.target)).delete()
                except GithubException as e:
                    if e.status == 404:
                        pr.get_review_comment(int(self.target)).delete()
                    else:
                        raise
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


class TaskBill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    discount_percent = models.FloatField(default=0)
    total_credits_used = models.FloatField(default=0)
    user_is_owner = models.BooleanField(default=False)
    project_is_open_source = models.BooleanField(default=False)

    @property
    def final_cost(self):
        """Final amounts of credits billed to the user after discounts"""
        if self.user_is_owner and self.project_is_open_source:
            return 0
        return self.total_credits_used * (1 - self.discount_percent)

    def __str__(self):
        return f"Bill for {self.task.title}"



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
