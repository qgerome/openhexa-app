# Generated by Django 3.2.7 on 2021-09-30 09:56

from django.db import migrations

import hexa.user_management.models


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0003_feature_flags"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", hexa.user_management.models.UserManager()),
            ],
        ),
    ]