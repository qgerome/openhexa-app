# Generated by Django 3.1.6 on 2021-03-19 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user_management", "0001_initial"),
        ("connector_dhis2", "0001_initial"),
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
                to="connector_dhis2.instance",
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
                to="connector_dhis2.indicatortype",
            ),
        ),
        migrations.AddField(
            model_name="indicator",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="connector_dhis2.instance",
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
                to="connector_dhis2.instance",
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
