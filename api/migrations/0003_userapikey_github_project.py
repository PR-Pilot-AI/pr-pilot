# Generated by Django 5.0.3 on 2024-04-18 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_userapikey_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='userapikey',
            name='github_project',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
