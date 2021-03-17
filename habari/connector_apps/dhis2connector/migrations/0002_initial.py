# Generated by Django 3.1.6 on 2021-03-17 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dhis2connector", "0001_initial"),
        ("user_management", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="instance",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="indicatortype",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="dhis2connector.instance",
            ),
        ),
        migrations.AddField(
            model_name="indicatortype",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="indicator",
            name="dhis2_indicator_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dhis2connector.indicatortype",
            ),
        ),
        migrations.AddField(
            model_name="indicator",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="dhis2connector.instance",
            ),
        ),
        migrations.AddField(
            model_name="indicator",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="dataelement",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="dhis2connector.instance",
            ),
        ),
        migrations.AddField(
            model_name="dataelement",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
    ]
