import uuid

from django.db import models

from engine.models.task import Task


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
        return self.total_credits_used * (1 - self.discount_percent)

    def __str__(self):
        return f"Bill for {self.task.title}"
