# Generated by Django 3.2.3 on 2021-05-24 15:30

from django.db import migrations, models
import hexa.core.models.cryptography


class Migration(migrations.Migration):

    dependencies = [
        ("connector_s3", "0003_datasource_urls"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bucket",
            old_name="sync_credentials",
            new_name="api_credentials",
        ),
        migrations.RemoveField(
            model_name="credentials",
            name="team",
        ),
        migrations.AddField(
            model_name="credentials",
            name="role_arn",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="credentials",
            name="access_key_id",
            field=hexa.core.models.cryptography.EncryptedTextField(),
        ),
        migrations.AlterField(
            model_name="credentials",
            name="secret_access_key",
            field=hexa.core.models.cryptography.EncryptedTextField(),
        ),
    ]