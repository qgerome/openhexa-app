# Generated by Django 3.2.4 on 2021-07-08 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_s3", "0009_datasource_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="credentials",
            name="default_region",
            field=models.CharField(default="", max_length=200),
        ),
    ]
