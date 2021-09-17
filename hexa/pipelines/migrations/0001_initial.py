# Generated by Django 3.2 on 2021-04-26 12:13

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PipelinesIndex",
            fields=[
                (
                    "index_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="core.index",
                    ),
                ),
                (
                    "index_type",
                    models.CharField(
                        choices=[
                            ("PIPELINES_ENVIRONMENT", "Pipeline environment"),
                            ("PIPELINES_PIPELINE", "Pipeline"),
                        ],
                        max_length=100,
                    ),
                ),
            ],
            options={
                "verbose_name": "Pipeline Index",
                "verbose_name_plural": "Pipeline indexes",
            },
            bases=("core.index",),
        ),
        migrations.CreateModel(
            name="PipelinesIndexPermission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "pipeline_index",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pipelines.pipelinesindex",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
