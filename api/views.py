from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    inline_serializer,
)
from github import Github
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import BaseHasAPIKey

from api.models import UserAPIKey
from api.serializers import PromptSerializer, TaskSerializer
from engine.models.task import Task, TaskType
from engine.task_scheduler import SchedulerError
from webhooks.jwt_tools import get_installation_access_token
from webhooks.models import GithubRepository

# Number of tasks to show in the task list
TASK_LIST_LIMIT = 10


class HasUserAPIKey(BaseHasAPIKey):
    model = UserAPIKey


@extend_schema(
    responses={
        status.HTTP_200_OK: TaskSerializer,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response=inline_serializer(
                name="NotFound",
                fields={"error": serializers.CharField()},
            ),
            examples=[
                OpenApiExample(
                    "TaskNotFound",
                    summary="Task Not Found",
                    description="The specified task does not exist",
                    value={"error": "Task not found"},
                )
            ],
            description="The specified task does not exist.",
        ),
    },
    tags=["Task Retrieval"],
)
@api_view(["GET"])
@permission_classes([HasUserAPIKey])
def get_task(request, pk):
    """Retrieve a task by ID."""
    api_key = UserAPIKey.objects.get_from_key(request.headers["X-Api-Key"])
    task = Task.objects.get(id=pk)
    if task.github_user != api_key.username:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = TaskSerializer(task)
    return Response(serializer.data)


class TaskViewSet(APIView):

    permission_classes = [HasUserAPIKey]

    @extend_schema(
        responses={
            status.HTTP_200_OK: TaskSerializer(many=True),
        },
        tags=["Task Retrieval"],
    )
    def get(self, request, pk=None):
        """List the last 10 tasks created by you."""
        api_key = UserAPIKey.objects.get_from_key(request.headers["X-Api-Key"])
        tasks = Task.objects.filter(github_user=api_key.username).order_by("-created")[
            :TASK_LIST_LIMIT
        ]
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=PromptSerializer,
        responses={
            status.HTTP_201_CREATED: TaskSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=inline_serializer(
                    name="NotFound",
                    fields={"error": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Repository Not Found",
                        summary="Repository Not Found",
                        description="PR Pilot is not installed for this repository",
                        value={
                            "error": "PR Pilot is not installed for this repository. "
                            "Please go to https://github.com/apps/pr-pilot-ai/installations/new to install PR Pilot."
                        },
                    )
                ],
                description="The specified repository does not exist.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=inline_serializer(
                    name="BadRequest",
                    fields={
                        "error": serializers.CharField(),
                        "details": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "ValidationError",
                        summary="Validation Error",
                        description="Input validation failed",
                        value={
                            "error": "Input validation failed",
                            "details": "<validation_errors>",
                        },
                    )
                ],
                description="The request data does not pass validation.",
            ),
        },
        tags=["Task Creation"],
    )
    def post(self, request):
        """Create a new task."""
        api_key = UserAPIKey.objects.get_from_key(request.headers["X-Api-Key"])
        serializer = PromptSerializer(data=request.data)
        if serializer.is_valid():
            github_user = api_key.username
            try:
                repo = GithubRepository.objects.get(
                    full_name=serializer.validated_data["github_repo"]
                )
            except GithubRepository.DoesNotExist:
                return Response(
                    {
                        "error": "PR Pilot is not installed for this repository. "
                        "Please go to https://github.com/apps/pr-pilot-ai/installations/new to install PR Pilot."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            branch = ""
            pr_base = None
            if serializer.validated_data.get("pr_number"):
                g = Github(
                    get_installation_access_token(repo.installation.installation_id)
                )
                pr = g.get_repo(repo.full_name).get_pull(
                    serializer.validated_data["pr_number"]
                )
                branch = pr.head.ref
                pr_base = pr.base.ref
            elif serializer.validated_data.get("branch"):
                branch = serializer.validated_data["branch"]

            task = Task.objects.create(
                title="A title",
                user_request=serializer.validated_data["prompt"],
                installation_id=repo.installation.installation_id,
                github_project=repo.full_name,
                issue_number=serializer.validated_data.get("issue_number"),
                pr_number=serializer.validated_data.get("pr_number"),
                head=branch,
                branch=branch,
                base=pr_base,
                task_type=TaskType.STANDALONE.value,
                github_user=github_user,
                gpt_model=serializer.validated_data["gpt_model"],
                image=serializer.validated_data.get("image"),
            )
            try:
                task.schedule()
            except SchedulerError as e:
                task.delete()
                return Response(
                    {"error": "Task could not be scheduled", "details": str(e)},
                    status=status.HTTP_409_CONFLICT,
                )
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
