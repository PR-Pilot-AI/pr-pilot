from django.core.management.base import BaseCommand
from sentry_sdk import configure_scope

from engine.models.task import Task
from engine.task_engine import TaskEngine


class Command(BaseCommand):
    help = 'Run a task.'

    def add_arguments(self, parser):
        parser.add_argument('task_id', type=str)

    def handle(self, *args, **options):
        task_id = options['task_id']
        task = Task.objects.get(id=task_id)
        engine = TaskEngine(task)
        with configure_scope() as scope:
            scope.set_tag("task_id", str(task.id))
            scope.set_tag("github_user", task.github_user)
            scope.set_tag("github_project", task.github_project)
            scope.set_tag("github_issue", task.issue_number)
            scope.set_tag("github_pr", task.pr_number)
            engine.run()
