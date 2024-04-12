import pytest
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey

from engine.models.task import Task

# Create your tests here.
client = APIClient()


@pytest.fixture
def api_key():
    api_key, key = APIKey.objects.create_key(name="for-testing")
    return key


@pytest.mark.django_db
def test_create_task_via_api(api_key):
    response = client.post('/api/tasks/', headers={'X-Api-Key': api_key}, data={'prompt': 'Hello, World!'})
    assert response.status_code == 201
    task = Task.objects.first()
    assert task is not None
    assert task.user_request == 'Hello, World!'