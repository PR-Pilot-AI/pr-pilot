from django.contrib.auth.models import AbstractUser
from django.db import models

class LinearIntegration(models.Model):
    # Define fields for LinearIntegration
    pass

class SlackIntegration(models.Model):
    # Define fields for SlackIntegration
    pass

class PilotUser(AbstractUser):
    linear_integration = models.OneToOneField(LinearIntegration, on_delete=models.CASCADE, null=True, blank=True)
    slack_integration = models.OneToOneField(SlackIntegration, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.linear_integration:
            self.linear_integration = LinearIntegration.objects.create()
        if not self.slack_integration:
            self.slack_integration = SlackIntegration.objects.create()
        super().save(*args, **kwargs)

class UserBudget(models.Model):
    username = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=500)

    @property
    def formatted(self):
        return f"{self.budget:.0f}"

    def __str__(self):
        return f"Budget {self.username} - ${self.budget}"

    @staticmethod
    def get_user_budget(username):
        try:
            return UserBudget.objects.get(username=username)
        except UserBudget.DoesNotExist:
            return UserBudget.objects.create(username=username)
