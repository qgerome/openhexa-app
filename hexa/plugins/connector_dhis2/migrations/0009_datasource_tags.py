# Generated by Django 3.2.4 on 2021-07-01 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_tags'),
        ('connector_dhis2', '0008_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='tags',
            field=models.ManyToManyField(to='catalog.Tag'),
        ),
    ]
