import logging
from functools import wraps
import os
import shutil
from django.conf import settings
import git

from engine.models.task import Task
from engine.models.task_event import TaskEvent
from webhooks.jwt_tools import get_installation_access_token


logger = logging.getLogger(__name__)


def needs_code_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        task = Task.current()
        TaskEvent.add(
            actor="assistant",
            action="clone_repo",
            target=task.github_project,
            message="Cloning repository",
        )
        logger.info(f"Cloning repo {task.github_project} to {settings.REPO_DIR}")
        if os.path.exists(settings.REPO_DIR):
            shutil.rmtree(settings.REPO_DIR)
        github_token = get_installation_access_token(task.installation_id)
        git_repo_url = f"https://x-access-token:{github_token}@github.com/{task.github_project}.git"
        git.Repo.clone_from(git_repo_url, settings.REPO_DIR)
        logger.info(f"Cloned repo {task.github_project} to {settings.REPO_DIR}")
        return func(*args, **kwargs)
    return wrapper
