# Generated by Django 3.2.3 on 2021-05-27 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("connector_dhis2", "0005_encrypted_credentials"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dataelement",
            name="last_synced_at",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="last_synced_at",
        ),
        migrations.RemoveField(
            model_name="indicatortype",
            name="last_synced_at",
        ),
    ]