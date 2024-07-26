import logging
import os
import threading

import redis

from accounts.models import UserBudget
from engine.job import KubernetesJob
from engine.util import run_task_in_background
from prpilot import settings

logger = logging.getLogger(__name__)


class SchedulerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TaskScheduler:

    def __init__(self, task):
        self.task = task
        self.context = self.task.context
        self.redis_queue = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
        )

    def user_budget_empty(self):
        budget = UserBudget.get_user_budget(self.task.github_user)
        return budget.budget <= 0

    def user_can_write(self) -> bool:
        """Check if the user has write access to the repository"""
        repo = self.task.github.get_repo(self.task.github_project)
        permission = repo.get_collaborator_permission(self.task.github_user)
        return permission == "write" or permission == "admin"

    def schedule(self):
        self.context.acknowledge_user_prompt()
        if self.user_budget_empty():
            logger.info(f"User {self.task.github_user} has no budget")
            message = (
                "You have used up your budget. Please visit the "
                "[Dashboard](https://app.pr-pilot.ai) to purchase more credits."
            )
            self.context.respond_to_user(message)
            raise SchedulerError(message)

        if not self.user_can_write():
            message = (
                f"Sorry @{self.task.github_user}, you must be a collaborator of `{self.task.github_project}` "
                f"to run commands on this project."
            )
            logger.info(f"User {self.task.github_user} does not have write access")
            self.context.respond_to_user(message)
            raise SchedulerError(message)

        if self.task.would_reach_rate_limit():
            message = (
                f"Sorry @{self.task.github_user}, the project `{self.task.github_project}` has reached the rate "
                f"limit of {settings.TASK_RATE_LIMIT} per {settings.TASK_RATE_LIMIT_WINDOW} minutes. Please "
                f"try again later."
            )
            logger.info(
                f"Project {self.task.github_project} has reached the rate limit"
            )
            self.context.respond_to_user(message)
            raise SchedulerError(message)

        if settings.JOB_STRATEGY == "thread":
            # In local development, just run the task in a background thread
            settings.TASK_ID = self.task.id
            os.environ["TASK_ID"] = str(self.task.id)
            logger.info(f"Running task in debug mode: {self.task.id}")
            thread = threading.Thread(
                target=run_task_in_background, args=(self.task.id,)
            )
            thread.start()
        elif settings.JOB_STRATEGY == "kubernetes":
            # In production, run the task in a Kubernetes job
            job = KubernetesJob(self.task)
            job.spawn()
        elif settings.JOB_STRATEGY == "log":
            # In testing, just log the task
            logger.info(f"Running task in log mode: {self.task.id}")
        elif settings.JOB_STRATEGY == "redis":
            logger.info(f"Scheduling task via Redis: {self.task.id}")
            self.redis_queue.rpush(settings.REDIS_QUEUE, str(self.task.id))
        else:
            raise ValueError(f"Invalid JOB_STRATEGY: {settings.JOB_STRATEGY}")

        self.task.status = "scheduled"
        self.task.save()
