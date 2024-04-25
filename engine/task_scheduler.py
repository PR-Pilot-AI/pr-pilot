import logging
import os
import threading
import redis

from accounts.models import UserBudget
from engine.job import KubernetesJob
from engine.util import run_task_in_background
from prpilot import settings


logger = logging.getLogger(__name__)


class TaskScheduler:

    def __init__(self, task):
        self.task = task
        self.context = self.task.context
        self.redis_queue = redis.Redis(host='localhost', port=6379, db=0)


    def user_budget_empty(self):
        budget = UserBudget.get_user_budget(self.task.github_user)
        return budget.budget <= 0


    def user_can_write(self) -> bool:
        """Check if the user has write access to the repository"""
        repo = self.task.github.get_repo(self.task.github_project)
        permission = repo.get_collaborator_permission(self.task.github_user)
        return permission == 'write' or permission == 'admin'


    def project_has_reached_rate_limit(self):
        """Check if the project has reached the rate limit"""
        rate_limit = self.task.github.get_rate_limit()
        return rate_limit.core.remaining == 0


    def schedule(self):
        self.context.acknowledge_user_prompt()
        if self.user_budget_empty():
            logger.info(f'User {self.task.github_user} has no budget')
            self.context.respond_to_user(
                "You have used up your budget. Please visit the [Dashboard](https://app.pr-pilot.ai) to purchase more credits.")
            self.task.status = "failed"
            self.task.save()
            return

        if not self.user_can_write():
            message = f"Sorry @{self.task.github_user}, you must be a collaborator of `{self.task.github_project}` to run commands on this project."
            self.context.respond_to_user(message)
            self.task.status = "failed"
            self.task.save()
            return

        if self.task.would_reach_rate_limit():
            message = (f"Sorry @{self.task.github_user}, the project `{self.task.github_project}` has reached the rate "
                       f"limit of {settings.TASK_RATE_LIMIT} per {settings.TASK_RATE_LIMIT_WINDOW} minutes. Please "
                       f"try again later.")
            self.context.respond_to_user(message)
            self.task.status = "failed"
            self.task.save()
            return

        # Enqueue task to Redis queue
        self.redis_queue.rpush('task_queue', self.task.id)

        self.task.status = "scheduled"
        self.task.save()

