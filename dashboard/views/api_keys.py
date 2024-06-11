from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from accounts.models import UserBudget
from api.models import UserAPIKey


class APIKeyForm(forms.Form):
    key_name = forms.CharField(
        label="Key Name (optional)",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter key name"}
        ),
    )


class APIKeyListView(LoginRequiredMixin, ListView):
    model = UserAPIKey
    template_name = "api_key_list.html"

    def get_queryset(self):
        # Filter the keys by the logged-in user's ID
        return UserAPIKey.objects.filter(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        budget = UserBudget.get_user_budget(self.request.user.username)
        context["budget"] = budget.formatted
        context["form"] = APIKeyForm()
        return context

    def post(self, request, *args, **kwargs):
        form = APIKeyForm(request.POST)
        if form.is_valid():
            api_key, key = UserAPIKey.objects.create_key(
                name=form.cleaned_data["key_name"], username=request.user.username
            )
            context = {
                "message": "API Key was successfully created!",
                "api_key_name": form.cleaned_data["key_name"],
                "api_key": key,
            }

            # Render the confirmation template with context
            return render(request, "api_key_confirmation.html", context)
        else:
            return self.get(self, request, *args, **kwargs)
