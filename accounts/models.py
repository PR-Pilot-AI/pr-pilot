from django.contrib.auth.models import AbstractUser
from django.db import models


class LinearIntegration(models.Model):
    access_token = models.TextField(null=True, blank=False)


class SlackIntegration(models.Model):
    bot_token = models.TextField(null=True, blank=False)
    user_token = models.TextField(null=True, blank=False)


class SentryIntegration(models.Model):
    api_key = models.TextField(null=True, blank=False)


class PilotUser(AbstractUser):
    linear_integration = models.OneToOneField(
        LinearIntegration, on_delete=models.CASCADE, null=True, blank=True
    )
    slack_integration = models.OneToOneField(
        SlackIntegration, on_delete=models.CASCADE, null=True, blank=True
    )
    sentry_integration = models.OneToOneField(
        SentryIntegration, on_delete=models.CASCADE, null=True, blank=True
    )


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
