# Generated by Django 3.2.6 on 2021-08-31 09:12

from django.db import migrations
import hexa.core.models.path


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0013_path_non_unique_temp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="index",
            name="path",
            field=hexa.core.models.path.PathField(blank=True, null=True),
        ),
    ]
