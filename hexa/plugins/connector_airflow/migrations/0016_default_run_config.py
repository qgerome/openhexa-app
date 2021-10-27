# Generated by Django 3.2.7 on 2021-10-27 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_airflow", "0015_dagrun_finetuning"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dag",
            name="sample_config",
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="dagrun",
            name="conf",
            field=models.JSONField(default=dict),
        ),
    ]
