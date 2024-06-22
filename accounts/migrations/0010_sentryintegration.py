from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_rename_api_key_linearintegration_access_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentryIntegration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='pilotuser',
            name='sentry_integration',
            field=models.OneToOneField(null=True, on_delete=models.CASCADE, to='accounts.SentryIntegration'),
        ),
    ]
