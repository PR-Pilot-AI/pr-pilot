import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Task

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_tasks():
    Task.objects.create(title="Task 1", description="Description 1", completed=False)
    Task.objects.create(title="Task 2", description="Description 2", completed=True)

@pytest.mark.django_db
def test_list_tasks(api_client, create_tasks):
    url = reverse('task-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['title'] == "Task 1"
    assert response.data[1]['title'] == "Task 2"
