from django.urls import path

import dashboard.views.api_keys
import dashboard.views.integrations
import dashboard.views.stripe
import dashboard.views.tasks

urlpatterns = [
    path(
        "refill/",
        dashboard.views.stripe.create_stripe_payment_link,
        name="refill_budget",
    ),
    path(
        "add-slack-integration/",
        dashboard.views.integrations.add_slack_integration,
        name="add_slack_integration",
    ),
    path(
        "add-linear-integration/",
        dashboard.views.integrations.add_linear_integration,
        name="add_linear_integration",
    ),
    path(
        "add-pr-pilot-integration/",
        dashboard.views.integrations.add_pr_pilot_integration,
        name="add_pr_pilot_integration",
    ),
    path("tasks/", dashboard.views.tasks.TaskListView.as_view(), name="task_list"),
    path(
        "integrations/",
        dashboard.views.integrations.IntegrationView.as_view(),
        name="integrations",
    ),
    path(
        "api-keys/",
        dashboard.views.api_keys.APIKeyListView.as_view(),
        name="api_key_list",
    ),
    path(
        "tasks/<uuid:pk>/",
        dashboard.views.tasks.TaskDetailView.as_view(),
        name="task_detail",
    ),
    path(
        "tasks/<uuid:pk>/undo/",
        dashboard.views.tasks.TaskUndoView.as_view(),
        name="task_undo",
    ),
]
