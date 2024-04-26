from django.core.management.base import BaseCommand

from engine.task_worker import TaskWorker


class Command(BaseCommand):
    help = "Run a task worker."

    def handle(self, *args, **options):
        worker = TaskWorker()
        worker.run()
