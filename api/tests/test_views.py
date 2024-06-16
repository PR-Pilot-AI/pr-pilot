import pytest
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey
from engine.models.task import Task
from api.models import UserAPIKey


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_key():
    api_key, key = UserAPIKey.objects.create_key(name="test-user", username="testuser")
    return key


@pytest.mark.django_db
def test_list_tasks(api_client, user_api_key):
    # Create some tasks for the test user
    Task.objects.create(title="Task 1", github_user="testuser")
    Task.objects.create(title="Task 2", github_user="testuser")
    Task.objects.create(title="Task 3", github_user="testuser")

    # Authenticate with the API key
    api_client.credentials(HTTP_X_API_KEY=user_api_key)

    # Make the request to the list_tasks endpoint
    response = api_client.get("/api/tasks/list/")

    # Check the response
    assert response.status_code == 200
    assert len(response.data) == 3
    assert response.data[0]["title"] == "Task 1"
    assert response.data[1]["title"] == "Task 2"
    assert response.data[2]["title"] == "Task 3"
