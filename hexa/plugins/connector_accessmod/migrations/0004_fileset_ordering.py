# Generated by Django 4.0.1 on 2022-01-28 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0003_accessmod_files"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fileset",
            options={"ordering": ["name"]},
        ),
    ]
