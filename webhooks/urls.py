from django.urls import path
from . import views

urlpatterns = [
    path('github', views.github_webhook, name='github_webhook'),
]
