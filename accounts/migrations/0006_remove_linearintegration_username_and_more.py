# Generated by Django 5.0.3 on 2024-06-07 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_linearintegration_slackintegration_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="linearintegration",
            name="username",
        ),
        migrations.RemoveField(
            model_name="slackintegration",
            name="username",
        ),
    ]
