# Generated by Django 3.1.6 on 2021-02-08 20:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0012_source_to_datasource"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dhis2dataelement",
            name="datasource",
            field=models.ForeignKey(
                limit_choices_to={"datasource_type": "DHIS2"},
                on_delete=django.db.models.deletion.CASCADE,
                to="catalog.datasource",
            ),
        ),
        migrations.AlterField(
            model_name="dhis2indicator",
            name="datasource",
            field=models.ForeignKey(
                limit_choices_to={"datasource_type": "DHIS2"},
                on_delete=django.db.models.deletion.CASCADE,
                to="catalog.datasource",
            ),
        ),
    ]
