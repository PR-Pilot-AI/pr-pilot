import logging
import os

import redis
from django.conf import settings
from sentry_sdk import configure_scope

from engine.models.task import Task
from engine.task_engine import TaskEngine

logger = logging.getLogger(__name__)


class TaskWorker:

    def __init__(self):
        self.redis_queue = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
        )

    def run(self):
        logger.info("Running task worker")
        while True:
            _, task_id = self.redis_queue.blpop([settings.REDIS_QUEUE])
            task_id = task_id.decode("utf-8")
            settings.TASK_ID = task_id
            os.environ["TASK_ID"] = task_id
            logger.info(f"Received task {task_id}")
            task = Task.objects.get(id=task_id)
            engine = TaskEngine(task)
            with configure_scope() as scope:
                scope.set_tag("task_id", str(task.id))
                scope.set_tag("github_user", task.github_user)
                scope.set_tag("github_project", task.github_project)
                scope.set_tag("github_issue", task.issue_number)
                scope.set_tag("github_pr", task.pr_number)
                engine.run()
