# Generated by Django 3.1.5 on 2021-01-19 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_renaming"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dhis2dataelement",
            name="dhis2_id",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="dhis2indicator",
            name="dhis2_id",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]