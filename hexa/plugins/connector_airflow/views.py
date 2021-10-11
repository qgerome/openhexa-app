import uuid

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.datagrids import RunGrid
from hexa.plugins.connector_airflow.datacards import ClusterCard, DAGCard, DAGRunCard
from hexa.plugins.connector_airflow.datagrids import DAGConfigGrid, DAGGrid
from hexa.plugins.connector_airflow.models import (  # DAGRunState,
    DAG,
    Cluster,
    DAGConfig,
    DAGRun,
    DAGRunState,
)


def cluster_detail(request: HttpRequest, cluster_id: uuid.UUID) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user),
        pk=cluster_id,
    )

    cluster_card = ClusterCard(cluster, request=request)
    if request.method == "POST" and cluster_card.save():
        return redirect(request.META["HTTP_REFERER"])

    dag_grid = DAGGrid(
        cluster.dag_set.all(), page=int(request.GET.get("page", "1")), request=request
    )

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster.name,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
    ]

    return render(
        request,
        "connector_airflow/cluster_detail.html",
        {
            "cluster": cluster,
            "cluster_card": cluster_card,
            "dag_grid": dag_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def cluster_detail_refresh(request: HttpRequest, cluster_id: uuid.UUID) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user),
        pk=cluster_id,
    )
    for dag in [dag for dag in cluster.dag_set.filter() if dag.last_run is not None]:
        dag.last_run.refresh()

    return cluster_detail(request, cluster_id=cluster_id)


def dag_detail(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_card = DAGCard(dag, request=request)
    if request.method == "POST" and dag_card.save():
        return redirect(request.META["HTTP_REFERER"])

    config_grid = DAGConfigGrid(
        DAGConfig.objects.filter_for_user(request.user).filter(dag=dag), request=request
    )
    run_grid = RunGrid(
        DAGRun.objects.filter_for_user(request.user)
        .filter(dag=dag)
        .order_by("-execution_date"),
        request=request,
    )

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
        (dag, "connector_airflow:dag_detail", cluster_id, dag_id),
    ]

    return render(
        request,
        "connector_airflow/dag_detail.html",
        {
            "dag": dag,
            "breadcrumbs": breadcrumbs,
            "dag_card": dag_card,
            "config_grid": config_grid,
            "run_grid": run_grid,
        },
    )


def new_dag_run(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_run = dag.run()

    return redirect(dag_run.get_absolute_url())


def dag_run_detail(
    request: HttpRequest,
    cluster_id: uuid.UUID,
    dag_id: uuid.UUID,
    dag_run_id: uuid.UUID,
) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_run = get_object_or_404(
        DAGRun.objects.filter_for_user(request.user), pk=dag_run_id
    )

    dag_run_card = DAGRunCard(dag_run, request=request)
    if request.method == "POST" and dag_run_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster.name,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
        (dag, "connector_airflow:dag_detail", cluster_id, dag_id),
        (f"Run {dag_run.run_id}",),
    ]

    return render(
        request,
        "connector_airflow/dag_run_detail.html",
        {
            "cluster": cluster,
            "dag_run_card": dag_run_card,
            "breadcrumbs": breadcrumbs,
        },
    )


def dag_detail_refresh(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    for run in dag.dagrun_set.filter(state=DAGRunState.RUNNING):
        run.refresh()

    return dag_detail(request, cluster_id=cluster_id, dag_id=dag_id)


def sync(request: HttpRequest, cluster_id: uuid.UUID):
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user), pk=cluster_id
    )

    sync_result = cluster.sync()
    messages.success(request, sync_result)

    return redirect(request.META.get("HTTP_REFERER", cluster.get_absolute_url()))
