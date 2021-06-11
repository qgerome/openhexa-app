# Generated by Django 3.2.3 on 2021-06-03 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_s3", "0005_sync_fine_tuning"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bucket",
            name="api_credentials",
        ),
        migrations.AlterField(
            model_name="credentials",
            name="role_arn",
            field=models.CharField(max_length=200),
        ),
    ]