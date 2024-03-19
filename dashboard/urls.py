from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns...
    path('refill/', views.create_stripe_payment_link, name='refill_budget'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/<uuid:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
]
