import base64

from rest_framework import serializers

from engine.models.task import Task


class Base64BinaryField(serializers.Field):
    def to_representation(self, value):
        # Convert binary data to base64
        return base64.b64encode(value).decode()

    def to_internal_value(self, data):
        # Convert base64 string to binary data
        size_in_kb = len(data) / 1024
        max_size = 200  # kb
        if size_in_kb > max_size:
            raise serializers.ValidationError(
                f"Image size is too large. Max size is {max_size} KB"
            )
        return base64.b64decode(data)


class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        required=True, allow_blank=False, help_text="The prompt for the task"
    )
    github_repo = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="The full name of the Github repository, e.g. 'owner/repo'",
    )
    issue_number = serializers.IntegerField(
        required=False,
        help_text="Number of the issue if task is triggered in the context of an issue",
    )
    pr_number = serializers.IntegerField(
        required=False,
        help_text="Number of the PR if task is triggered in the context of a PR",
    )
    gpt_model = serializers.CharField(
        required=False,
        default="gpt-4-turbo",
        help_text="The GPT model to use for the task",
    )
    image = Base64BinaryField(
        required=False, help_text="An image to be used in the task"
    )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "user_request",
            "github_project",
            "github_user",
            "status",
            "created",
            "result",
            "issue_number",
            "pr_number",
            "gpt_model",
        ]
