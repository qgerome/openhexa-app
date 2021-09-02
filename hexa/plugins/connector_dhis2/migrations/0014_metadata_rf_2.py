# Generated by Django 3.2.6 on 2021-08-23 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("connector_dhis2", "0013_metadata_rf_1"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dataelement",
            options={"ordering": ("name",), "verbose_name": "DHIS2 Data Element"},
        ),
        migrations.AlterModelOptions(
            name="indicator",
            options={"ordering": ("name",), "verbose_name": "DHIS2 Indicator"},
        ),
        migrations.AlterModelOptions(
            name="indicatortype",
            options={"ordering": ("name",), "verbose_name": "DHIS2 Indicator type"},
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_aggregation_type",
            new_name="aggregation_type",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_code",
            new_name="code",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_created",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_description",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_domain_type",
            new_name="domain_type",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_external_access",
            new_name="external_access",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_favorite",
            new_name="favorite",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_last_updated",
            new_name="last_updated",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_name",
            new_name="name",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_short_name",
            new_name="short_name",
        ),
        migrations.RenameField(
            model_name="dataelement",
            old_name="dhis2_value_type",
            new_name="value_type",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_annualized",
            new_name="annualized",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_code",
            new_name="code",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_created",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_description",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_external_access",
            new_name="external_access",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_favorite",
            new_name="favorite",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_indicator_type",
            new_name="indicator_type",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_last_updated",
            new_name="last_updated",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_name",
            new_name="name",
        ),
        migrations.RenameField(
            model_name="indicator",
            old_name="dhis2_short_name",
            new_name="short_name",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_created",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_description",
            new_name="description",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_external_access",
            new_name="external_access",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_factor",
            new_name="factor",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_favorite",
            new_name="favorite",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_last_updated",
            new_name="last_updated",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_name",
            new_name="name",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_number",
            new_name="number",
        ),
        migrations.RenameField(
            model_name="indicatortype",
            old_name="dhis2_short_name",
            new_name="short_name",
        ),
    ]
