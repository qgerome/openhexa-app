# Generated by Django 3.1.7 on 2021-04-14 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("connector_s3", "0001_initial"),
        ("user_management", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="object",
            name="hexa_owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="object",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="connector_s3.bucket"
            ),
        ),
        migrations.AddField(
            model_name="object",
            name="parent",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="connector_s3.object",
            ),
        ),
        migrations.AddField(
            model_name="credentials",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="user_management.team",
            ),
        ),
        migrations.AddField(
            model_name="bucketpermission",
            name="bucket",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="connector_s3.bucket"
            ),
        ),
        migrations.AddField(
            model_name="bucketpermission",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user_management.team"
            ),
        ),
        migrations.AddField(
            model_name="bucket",
            name="hexa_owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user_management.organization",
            ),
        ),
        migrations.AddField(
            model_name="bucket",
            name="sync_credentials",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="connector_s3.credentials",
            ),
        ),
    ]