import json
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from hexa.core.models import Base, WithStatus, Permission, RichContent
from hexa.core.models.cryptography import EncryptedTextField
from hexa.pipelines.models import (
    Environment as BaseEnvironment,
    PipelinesIndex,
    PipelinesIndexPermission,
    Pipeline,
    PipelinesIndexType,
)


class Credentials(Base):
    """This class is a temporary way to store GCP Airflow credentials. This approach is not safe for production,
    as credentials are not encrypted.
    TODO: Store credentials in a secure storage engine like Vault.
    TODO: Handle different kind of credentials (not just OIDC)
    """

    OIDC_TARGET_AUDIENCE_DOC_URL = (
        "https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf"
        "#get_the_client_id_of_the_iam_proxy"
    )
    OIDC_TARGET_AUDIENCE_HELP_TEXT = (
        f'Corresponds to the <a href="{OIDC_TARGET_AUDIENCE_DOC_URL}" target="_blank">'
        f"client_id of the IAM Proxy</a>"
    )

    class Meta:
        verbose_name_plural = "Credentials"
        ordering = ("service_account_email",)

    service_account_email = EncryptedTextField()
    service_account_key_data = EncryptedTextField(
        help_text="The content of the JSON key in GCP"
    )
    oidc_target_audience = models.CharField(
        max_length=200,
        blank=False,
        help_text=OIDC_TARGET_AUDIENCE_HELP_TEXT,
    )

    @property
    def display_name(self):
        return self.service_account_email


class ClusterQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            clusterpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class Cluster(BaseEnvironment):
    class Meta:
        ordering = (
            "name",
            "airflow_name",
        )

    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )
    airflow_name = models.CharField(max_length=200)
    airflow_web_url = models.URLField(blank=False)
    airflow_api_url = models.URLField()

    objects = ClusterQuerySet.as_manager()

    def index(self):
        pipeline_index, _ = PipelinesIndex.objects.update_or_create(
            defaults={
                "owner": self.owner,
                "name": self.name,
                "external_name": self.airflow_name,
                "countries": self.countries,
                "content_summary": self.content_summary,
            },
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            index_type=PipelinesIndexType.PIPELINES_ENVIRONMENT,
            detail_url=reverse("connector_airflow:cluster_detail", args=(self.pk,)),
        )

        for permission in self.clusterpermission_set.all():
            PipelinesIndexPermission.objects.get_or_create(
                pipeline_index=pipeline_index, team=permission.team
            )

    @property
    def content_summary(self):
        count = self.dag_set.count()

        return (
            ""
            if count == 0
            else _("%(dag_count)d DAG%(suffix)s")
            % {"dag_count": count, "suffix": pluralize(count)}
        )


class ClusterPermission(Permission):
    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("cluster", "team")]

    def index_object(self):
        self.cluster.index()

    def __str__(self):
        return f"Permission for team '{self.team}' on cluster '{self.cluster}'"


class DAGQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            cluster__clusterpermission__team__in=[t.pk for t in user.team_set.all()]
        )


class DAG(Pipeline):
    class Meta:
        verbose_name = "DAG"
        ordering = ["airflow_id"]

    cluster = models.ForeignKey("Cluster", on_delete=models.CASCADE)
    airflow_id = models.CharField(max_length=200, blank=False)

    objects = DAGQuerySet.as_manager()

    @property
    def last_run(self):
        return DAGConfigRun.objects.get_last_for_dag_and_config(dag=self)

    @property
    def content_summary(self):
        count = self.dagconfig_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d DAG configuration%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )


class DAGConfigQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag__cluster__clusterpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )


class DAGConfig(RichContent):
    class Meta:
        verbose_name = "DAG config"

    dag = models.ForeignKey("DAG", on_delete=models.CASCADE)
    config_data = models.JSONField(default=dict)

    objects = DAGConfigQuerySet.as_manager()

    @property
    def content_summary(self):
        count = self.dagconfigrun_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d DAG configuration%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    @property
    def last_run(self):
        return DAGConfigRun.objects.get_last_for_dag_and_config(dag_config=self)

    def run(self):
        # TODO: move in API module
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        # as well as https://cloud.google.com/composer/docs/samples/composer-get-environment-client-id
        api_credentials = self.dag.cluster.api_credentials
        service_account_key_data = json.loads(api_credentials.service_account_key_data)
        id_token_credentials = (
            service_account.IDTokenCredentials.from_service_account_info(
                service_account_key_data,
                target_audience=api_credentials.oidc_target_audience,
            )
        )
        session = AuthorizedSession(id_token_credentials)
        dag_config_run_id = str(uuid.uuid4())
        api_url = self.dag.cluster.airflow_api_url
        response = session.post(
            f"{api_url.rstrip('/')}/dags/{self.dag.airflow_id}/dag_runs",
            data=json.dumps(
                {
                    "conf": self.config_data,
                    "run_id": dag_config_run_id,
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        # TODO: handle non-200
        response_data = response.json()

        DAGConfigRun.objects.create(
            id=dag_config_run_id,
            dag_config=self,
            last_refreshed_at=timezone.now(),
            airflow_run_id=response_data["run_id"],
            airflow_execution_date=response_data["execution_date"],
            airflow_message=response_data["message"],
            airflow_state=DAGConfigRunState.RUNNING,
        )

        self.last_run_at = timezone.now()
        self.save()

        return DAGConfigRunResult(self)


class DAGConfigRunResult:
    # TODO: document and move in api module

    def __init__(self, dag_config):
        self.dag_config = dag_config

    def __str__(self):
        return _('The DAG config "%(name)s" has been run') % {
            "name": self.dag_config.display_name
        }


class DAGConfigRunQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            dag_config__dag__cluster__clusterpermission__team__in=[
                t.pk for t in user.team_set.all()
            ]
        )

    def filter_by_dag(self, dag):
        return self.filter(dag_config__dag=dag)

    def get_last_for_dag_and_config(self, *, dag=None, dag_config=None):
        qs = self.all()
        if dag is not None:
            qs = qs.filter(dag_config__dag=dag)
        if dag_config is not None:
            qs = qs.filter(dag_config=dag_config)

        return qs.order_by("-airflow_execution_date").first()


class DAGConfigRunState(models.TextChoices):
    SUCCESS = "success", _("Success")
    RUNNING = "running", _("Running")
    FAILED = "failed", _("Failed")


class DAGConfigRun(Base, WithStatus):
    STATUS_MAPPINGS = {
        DAGConfigRunState.SUCCESS: WithStatus.SUCCESS,
        DAGConfigRunState.RUNNING: WithStatus.PENDING,
        DAGConfigRunState.FAILED: WithStatus.ERROR,
    }

    class Meta:
        ordering = ("-last_refreshed_at",)

    dag_config = models.ForeignKey("DAGConfig", on_delete=models.CASCADE)
    last_refreshed_at = models.DateTimeField(null=True)
    airflow_run_id = models.CharField(max_length=200, blank=False)
    airflow_message = models.TextField()
    airflow_execution_date = models.DateTimeField()
    airflow_state = models.CharField(
        max_length=200, blank=False, choices=DAGConfigRunState.choices
    )

    objects = DAGConfigRunQuerySet.as_manager()

    def refresh(self):
        # TODO: move in api module
        # See https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf
        # and https://google-auth.readthedocs.io/en/latest/user-guide.html#identity-tokens
        api_credentials = self.dag_config.dag.cluster.api_credentials
        service_account_key_data = json.loads(api_credentials.service_account_key_data)
        id_token_credentials = (
            service_account.IDTokenCredentials.from_service_account_info(
                service_account_key_data,
                target_audience=api_credentials.oidc_target_audience,
            )
        )
        session = AuthorizedSession(id_token_credentials)
        api_url = self.dag_config.dag.cluster.airflow_api_url
        execution_date = self.airflow_execution_date.isoformat()
        response = session.get(
            f"{api_url.rstrip('/')}/dags/{self.dag_config.dag.airflow_id}/dag_runs/{execution_date}",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        # TODO: handle non-200
        response_data = response.json()

        self.last_refreshed_at = timezone.now()
        self.airflow_state = response_data["state"]
        self.save()

    @property
    def status(self):
        try:
            return self.STATUS_MAPPINGS[self.airflow_state]
        except KeyError:
            return WithStatus.UNKNOWN
