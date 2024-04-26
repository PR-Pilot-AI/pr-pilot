from django.db import migrations


def multiply_price(apps, schema_editor):
    UserBudget = apps.get_model(
        "accounts", "UserBudget"
    )  # Replace 'your_app_name' with the actual app name
    for budget in UserBudget.objects.all():
        budget.budget *= 100
        budget.save(update_fields=["budget"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_userbudget"),
    ]

    operations = [
        migrations.RunPython(multiply_price),
    ]
