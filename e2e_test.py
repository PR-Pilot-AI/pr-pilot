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


def create_task(prompt, model):
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


TIME_FRAME = "June 2024"
EXECUTIVE_SUMMARY = f"""
I want an executive summary of activity in Slack, on Github and in Linear for {TIME_FRAME}.

Collect the following information:
- All Slack messages of {TIME_FRAME} in the #bot-testing, #general and #random channels.
- All Github issues and PRs in {TIME_FRAME}.
- All Linear comments and issues created or edited in {TIME_FRAME}.

Respond with a report that includes:
- A one-paragraph summary of all activity
- An "Urgent Items" section with anything that requires immediate attention (include links)
- A "Topics" section that lists the most discussed topics
"""
COPY_ISSUE = """
Find the latest Github issue labeled 'bug' and copy it to Linear.
"""
ALL_LINEAR_LISSUES = f"""
Find all Linear issues of {TIME_FRAME}.
"""

POST_ISSUES_TO_SLACK = """
Find all Linear issues created since yesterday.
Summarize them in the following way:
- Title: "Linear issues created since <date>"
- One concise paragraph summary of all issues
- A list of all issue titles as links
- Each link begins with an emoji that represents the issue type (bug, feature, etc.)

Send the summary to #bot-testing on Slack.
Respond with a link to the Slack message.
"""


def run_e2e_test():
    task = create_task(
        "Scramble the readme file",
        model="gpt-4o",
    )
    settings.TASK_ID = str(task.id)
    os.environ["TASK_ID"] = str(task.id)
    engine = TaskEngine(task)
    engine.run()
    print(task.result)


if __name__ == "__main__":
    run_e2e_test()
