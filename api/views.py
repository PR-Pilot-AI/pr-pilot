from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import BaseHasAPIKey

from api.models import UserAPIKey
from api.serializers import PromptSerializer, TaskSerializer
from engine.models.task import Task, TaskType
from webhooks.models import GithubRepository


class HasUserAPIKey(BaseHasAPIKey):
    model = UserAPIKey


@extend_schema(
    request=PromptSerializer,
    responses={
        status.HTTP_201_CREATED: TaskSerializer,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response=inline_serializer(
                name="Not Found",
                fields={"error": serializers.CharField()},
            ),
            examples=[OpenApiExample(
                "Repository Not Found",
                summary="Repository Not Found",
                description="PR Pilot is not installed for this repository",
                value={"error": "PR Pilot is not installed for this repository"},
            )],
            description='The specified repository does not exist.'
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            response=inline_serializer(
                name="Bad Request",
                fields={"error": serializers.CharField(),
                        "details": serializers.CharField()},
            ),
            examples=[OpenApiExample(
                "Validation Error",
                summary="Validation Error",
                description="Input validation failed",
                value={"error": "Input validation failed", "details": "<validation_errors>"},
            )],
            description='The request data does not pass validation.'
        ),
    },
    tags=['Task Creation'],
)
@api_view(['POST'])
@permission_classes([HasUserAPIKey])
def create_task(request):
    api_key = UserAPIKey.objects.get_from_key(request.headers['X-Api-Key'])
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        github_user = api_key.username
        try:
            repo = GithubRepository.objects.get(full_name=serializer.validated_data['github_repo'])
        except GithubRepository.DoesNotExist:
            return Response({'error': 'PR Pilot is not installed for this repository'},
                            status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(title="A title", user_request=serializer.validated_data['prompt'],
                                   installation_id=repo.installation.installation_id, github_project=repo.full_name,
                                   task_type=TaskType.STANDALONE.value,
                                   github_user=github_user)
        task.schedule()
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        status.HTTP_200_OK: TaskSerializer,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response=inline_serializer(
                name="Not Found",
                fields={"error": serializers.CharField()},
            ),
            examples=[OpenApiExample(
                "Task Not Found",
                summary="Task Not Found",
                description="The specified task does not exist",
                value={"error": "Task not found"},
            )],
            description='The specified task does not exist.'
        ),
    },
    tags=['Task Retrieval'],
)
@api_view(['GET'])
@permission_classes([HasUserAPIKey])
def get_task(request, pk):
    api_key = UserAPIKey.objects.get_from_key(request.headers['X-Api-Key'])
    task = Task.objects.get(id=pk)
    if task.github_user != api_key.username:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TaskSerializer(task)
    return Response(serializer.data)