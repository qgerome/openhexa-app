# Generated by Django 3.2.7 on 2021-09-28 09:26

import django.db.models.deletion
from django.db import migrations, models

import hexa.core.models.cryptography


class Migration(migrations.Migration):

    dependencies = [
        ("connector_airflow", "0009_dagconfig_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cluster",
            old_name="web_url",
            new_name="url",
        ),
        migrations.RemoveField(
            model_name="cluster",
            name="api_credentials",
        ),
        migrations.RemoveField(
            model_name="cluster",
            name="api_url",
        ),
        migrations.AddField(
            model_name="cluster",
            name="password",
            field=hexa.core.models.cryptography.EncryptedTextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cluster",
            name="username",
            field=hexa.core.models.cryptography.EncryptedTextField(default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="dagrun",
            name="dag_config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="connector_airflow.dagconfig",
            ),
        ),
        migrations.DeleteModel(
            name="Credentials",
        ),
    ]
