# flake8: noqa: E402

import logging
import os
import django

django.setup()

from django.conf import settings

from webhooks.models import GithubRepository

from engine.models.task import Task
from engine.task_engine import TaskEngine

logger = logging.getLogger(__name__)


def load_image(file_path="api/tests/fixtures/screenshot.png"):
    with open(file_path, "rb") as f:
        return f.read()


def create_task(prompt):
    github_project = "mlamina/DarwinGPT"
    repo = GithubRepository.objects.get(full_name=github_project)
    return Task.objects.create(
        user_request=prompt,
        installation_id=repo.installation.installation_id,
        pilot_command="Tell me what's in the image",
        github_user="mlamina",
        github_project=github_project,
        # image=load_image(),
    )


def run_e2e_test():
    task = create_task(
        "Find all Linear tickets that were edited over the last 24 hours."
    )
    settings.TASK_ID = str(task.id)
    os.environ["TASK_ID"] = str(task.id)
    engine = TaskEngine(task)
    engine.run()
    print(task.result)


if __name__ == "__main__":
    run_e2e_test()
