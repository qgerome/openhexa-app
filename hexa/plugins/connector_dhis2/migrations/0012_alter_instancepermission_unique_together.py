# Generated by Django 3.2.6 on 2021-08-10 08:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0001_initial"),
        ("connector_dhis2", "0011_alter_instance_tags"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="instancepermission",
            unique_together={("instance", "team")},
        ),
    ]
