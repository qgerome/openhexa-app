# Generated by Django 3.2.3 on 2021-05-24 16:17

from django.db import migrations
import hexa.core.models.cryptography


class Migration(migrations.Migration):

    dependencies = [
        ("connector_airflow", "0003_better_help_text"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="credentials",
            name="team",
        ),
        migrations.AlterField(
            model_name="credentials",
            name="service_account_email",
            field=hexa.core.models.cryptography.EncryptedTextField(),
        ),
        migrations.AlterField(
            model_name="credentials",
            name="service_account_key_data",
            field=hexa.core.models.cryptography.EncryptedTextField(
                help_text="The content of the JSON key in GCP"
            ),
        ),
    ]