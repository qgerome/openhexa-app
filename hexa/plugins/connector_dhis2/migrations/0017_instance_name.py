# Generated by Django 3.2.6 on 2021-08-31 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_dhis2", "0016_instance_locale"),
    ]

    operations = [
        migrations.AddField(
            model_name="instance",
            name="name",
            field=models.TextField(default="Missing name"),
            preserve_default=False,
        ),
    ]
