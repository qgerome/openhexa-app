# Generated by Django 3.2.6 on 2021-08-31 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_postgresql", "0004_auto_20210823_0906"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="rows",
            field=models.IntegerField(default=0),
        ),
    ]
