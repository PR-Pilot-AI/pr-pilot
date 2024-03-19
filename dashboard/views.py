import markdown
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from django_tables2 import SingleTableView
from django.urls import reverse
import stripe
from django.conf import settings

from accounts.models import UserBudget
from dashboard.tables import TaskTable, EventTable, CostItemTable
from engine.models import Task


# Create your views here.
class TaskListView(LoginRequiredMixin, SingleTableView):
    model = Task
    table_class = TaskTable
    template_name = 'task_list.html'

    def get_queryset(self):
        # Filter the tasks by the logged-in user's ID
        return Task.objects.filter(github_user=self.request.user.username)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        budget = UserBudget.get_user_budget(self.request.user.username)
        context['budget'] = budget.formatted
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        # Filter the queryset to only include tasks owned by the logged-in user
        return Task.objects.filter(github_user=self.request.user.username)

    def get_object(self, queryset=None):
        """Override get_object to ensure task ownership."""
        if queryset is None:
            queryset = self.get_queryset()
        # Make sure to catch the task based on the passed ID and check ownership
        pk = self.kwargs.get(self.pk_url_kwarg)
        task = get_object_or_404(queryset, pk=pk)

        # Check if the task belongs to the logged-in user
        if task.github_user != self.request.user.username:
            raise Http404("You do not have permission to view this task.")

        return task

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Get the task from the context
        task = context['task']
        # Create an EventTable instance with the task's events
        budget = UserBudget.get_user_budget(self.request.user.username)
        context['budget'] = budget.formatted
        context['event_table'] = EventTable(task.events.all())
        context['cost_item_table'] = CostItemTable(task.cost_items.all())
        context['task_result'] = mark_safe(markdown.markdown(task.result))
        context['total_cost'] = sum([item.credits for item in task.cost_items.all()])
        return context


@login_required
def create_stripe_payment_link(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('account_login'))

    # Get 'credits' query param
    credits = request.GET.get('credits')
    if not credits:
        return HttpResponseRedirect(reverse('task_list'))

    stripe.api_key = settings.STRIPE_API_KEY
    payment_link = stripe.PaymentLink.create(
        line_items=[{'price': 'price_1OvuaJCyRBEZZGEuL8I9b308', 'quantity': int(credits)}],
        after_completion={
            "type": "redirect",
            "redirect": {"url": "https://app.pr-pilot.ai/dashboard/"}
        },
        metadata={
            'github_user': request.user.username,
            'credits': int(credits),
        },
    )

    return HttpResponseRedirect(payment_link.url)
