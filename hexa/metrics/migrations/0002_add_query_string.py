# Generated by Django 3.2.7 on 2021-12-07 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metrics", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="request",
            options={"ordering": ["-response_time"]},
        ),
        migrations.AddField(
            model_name="request",
            name="query_string",
            field=models.TextField(default=""),
        ),
    ]