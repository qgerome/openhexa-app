# Generated by Django 3.2.3 on 2021-05-24 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="catalogindex",
            options={
                "ordering": ("name",),
                "verbose_name": "Catalog Index",
                "verbose_name_plural": "Catalog indexes",
            },
        ),
    ]
