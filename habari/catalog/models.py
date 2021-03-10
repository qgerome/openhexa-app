from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from functools import lru_cache

from habari.catalog.connectors import (
    get_connector_app_configs,
    get_connector_app_config,
)
from habari.common.models import (
    Base,
    DynamicTextChoices,
    PostgresTextSearchConfigField,
    Descriptive,
)
from habari.common.search import SearchResult


class DatasourceType(DynamicTextChoices):
    @staticmethod
    @lru_cache
    def build_choices():
        choices = {}
        for app in get_connector_app_configs():
            if app.datasource_type is not None:
                choices[app.datasource_type] = (
                    app.datasource_type,
                    _(app.datasource_type),
                )

        return choices


class DatasourceSearchResult(SearchResult):
    @property
    def result_type(self):
        return "datasource"

    @property
    def title(self):
        return self.model.name

    @property
    def label(self):
        return _("Datasource")

    @property
    def origin(self):
        return self.model.name

    @property
    def detail_url(self):
        app_config = get_connector_app_config(self.model)

        return reverse(f"{app_config.label}:datasource_detail", args=[self.model.pk])

    @property
    def updated_at(self):
        return self.model.updated_at

    @property
    def symbol(self):
        return f"{settings.STATIC_URL}img/icons/database.svg"


class DatasourceQuerySet(models.QuerySet):
    def search(self, query, *, limit=10, search_type=None):
        if search_type is not None and search_type != "datasource":
            return []

        search_vector = SearchVector("name", "short_name", "description", "countries")
        search_query = SearchQuery(query)
        search_rank = SearchRank(vector=search_vector, query=search_query)
        queryset = (
            self.annotate(rank=search_rank).filter(rank__gt=0).order_by("-rank")[:limit]
        )

        return [DatasourceSearchResult(datasource) for datasource in queryset]


class Datasource(Descriptive):
    class NoConnector(Exception):
        pass

    owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    datasource_type = models.CharField(choices=DatasourceType.choices, max_length=100)
    url = models.URLField(blank=True)
    active_from = models.DateTimeField(null=True, blank=True)
    active_to = models.DateTimeField(null=True, blank=True)
    public = models.BooleanField(default=False, verbose_name="Public dataset")
    last_synced_at = models.DateTimeField(null=True, blank=True)
    text_search_config = PostgresTextSearchConfigField()

    objects = DatasourceQuerySet.as_manager()

    def sync(self):
        """Sync the datasource using its connector"""

        try:
            sync_result = self.connector.sync()
            self.last_synced_at = timezone.now()
            self.save()

            return sync_result
        except ObjectDoesNotExist:
            raise Datasource.NoConnector(
                f'The datasource "{self.display_name}" has no connection'
            )

    @property
    def content_summary(self):
        try:
            return self.connector.get_content_summary()
        except ObjectDoesNotExist:
            return None

    @property
    def just_synced(self):
        return (
            self.last_synced_at is not None
            and (timezone.now() - self.last_synced_at).seconds < 60
        )


class ConnectorQuerySet(models.QuerySet):
    def search(self, query):
        return []


class Connector(Base):
    class Meta:
        abstract = True

    datasource = models.OneToOneField(
        "catalog.Datasource", on_delete=models.CASCADE, related_name="connector"
    )


class ExternalContent(Base):
    class Meta:
        abstract = True

    external_id = models.CharField(max_length=100, unique=True)
    datasource = models.ForeignKey(
        "catalog.Datasource",
        on_delete=models.CASCADE,
    )

    @property
    def display_name(self):
        raise NotImplementedError(
            f"Every catalog external content class should implement display_name()"
        )

    def __str__(self):
        return self.display_name
