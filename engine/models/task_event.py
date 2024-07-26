import logging
import uuid

from django.conf import settings
from django.db import models
from github import GithubException

from engine.channels import broadcast

logger = logging.getLogger(__name__)


class TaskEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="events")
    timestamp = models.DateTimeField(auto_now_add=True)
    reversed = models.BooleanField(default=False)
    actor = models.CharField(max_length=200)
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def undo(self):
        if self.action == "create_github_issue":
            logger.info(f"Closing issue {self.target}")
            self.task.github.get_repo(self.task.github_project).get_issue(
                int(self.target)
            ).edit(state="closed")
            TaskEvent.add(
                actor="assistant",
                action="close_github_issue",
                target=self.target,
                message="Closed github issue",
                task_id=self.task.id,
            )
            self.reversed = True
            self.save()
        elif self.action == "create_pull_request":
            logger.info(f"Closing pull request {self.target}")
            self.task.github.get_repo(self.task.github_project).get_pull(
                int(self.target)
            ).edit(state="closed")
            TaskEvent.add(
                actor="assistant",
                action="close_pull_request",
                target=self.target,
                message="Closed pull request",
                task_id=self.task.id,
            )
            self.reversed = True
            self.save()
        elif self.action == "comment_on_issue":
            logger.info(f"Deleting comment {self.target}")
            if self.task.pr_number:
                pr = self.task.github.get_repo(self.task.github_project).get_pull(
                    self.task.pr_number
                )
                try:
                    pr.get_issue_comment(int(self.target)).delete()
                except GithubException as e:
                    if e.status == 404:
                        pr.get_review_comment(int(self.target)).delete()
                    else:
                        raise
            else:
                issue = self.task.github.get_repo(self.task.github_project).get_issue(
                    self.task.issue_number
                )
                issue.get_comment(int(self.target)).delete()
            TaskEvent.add(
                actor="assistant",
                action="delete_github_comment",
                target=self.target,
                message="Deleted github comment",
                task_id=self.task.id,
            )
            self.reversed = True
            self.save()

    @property
    def reversible(self):
        reversible_actions = [
            "create_github_issue",
            "create_pull_request",
            "comment_on_issue",
        ]
        return self.action in reversible_actions

    @staticmethod
    def add(
        actor: str,
        action: str,
        target: str = None,
        message="",
        task_id=None,
        transaction=None,
        changes=[],
    ):
        if not task_id:
            task_id = settings.TASK_ID
        if not task_id:
            raise ValueError(
                "No task ID was provided. Please set TASK_ID in the environment or pass it as an argument."
            )
        new_entry = TaskEvent(
            actor=actor, action=action, target=target, message=message, task_id=task_id
        )
        new_entry.save()
        new_entry.broadcast()
        return new_entry

    def broadcast(self):
        broadcast(
            str(self.task_id),
            {
                "type": "event",
                "data": {
                    "id": str(self.id),
                    "actor": self.actor,
                    "action": self.action,
                    "target": self.target,
                    "message": self.message,
                    "timestamp": self.timestamp.isoformat(),
                },
            },
        )
