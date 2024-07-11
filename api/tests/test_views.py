from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Task, UserAPIKey
from django.contrib.auth.models import User

class TaskViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.api_key = UserAPIKey.objects.create(user=self.user, name="testkey")
        self.task = Task.objects.create(name="Test Task", github_user=self.user.username)
        self.url = reverse('delete_task', kwargs={'pk': self.task.id})

    def test_delete_task(self):
        self.client.credentials(HTTP_X_API_KEY=str(self.api_key.key))
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
