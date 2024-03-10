# Generated by Django 5.0.2 on 2024-03-10 01:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0005_task_comment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskevent',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='engine.task'),
        ),
    ]