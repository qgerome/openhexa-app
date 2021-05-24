# Generated by Django 3.2.3 on 2021-05-24 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_index_content_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='index',
            name='detail_url',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='index',
            name='external_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='index',
            name='name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
