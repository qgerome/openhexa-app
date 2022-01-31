# Generated by Django 4.0 on 2022-01-08 15:22

from django.db import migrations


def remove_dags(apps, schema_editor):
    # Clean up dags/dagruns present to bypass the need to data migrate
    # non-nullable FK. we will re-import them afterward anyway

    DAG = apps.get_model("connector_airflow", "DAG")
    for dag in DAG.objects.all():
        dag.delete()

    Index = apps.get_model("pipelines", "Index")
    for index in Index.objects.all():
        if index.object is None:
            index.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0006_forced_feature_flags"),
        ("connector_airflow", "0019_dag_run_user"),
        ("pipelines", "0008_indexes_django_4"),
    ]

    operations = [
        migrations.RunPython(remove_dags, lambda *a, **kwargs: None),
    ]
