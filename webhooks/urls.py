from django.urls import path
from . import views

urlpatterns = [
    path('github/', views.github_webhook, name='github_webhook'),
    path('stripe/', views.stripe_webhook, name='stripe_webhook'),
]
