# Generated by Django 3.2.6 on 2021-08-10 08:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0001_initial"),
        ("connector_airflow", "0005_longer_text_fields"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="clusterpermission",
            unique_together={("cluster", "team")},
        ),
    ]
