from logging import getLogger

from dhis2 import ClientException, RequestException
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import QuerySet
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import CatalogQuerySet, Datasource, Entry
from hexa.core.models import Base, Permission
from hexa.core.models.locale import LocaleField
from hexa.core.models.path import PathField

from ...catalog.sync import DatasourceSyncResult
from ...core.date_utils import date_format
from ...core.models.cryptography import EncryptedTextField
from .api import Dhis2Client
from .sync import sync_from_dhis2_results

logger = getLogger(__name__)


def validate_dhis2_base_url(value):
    if value.endswith("/"):
        raise ValidationError("DHIS2 url should not end with a '/'")


class Credentials(Base):
    class Meta:
        verbose_name = "DHIS2 API Credentials"
        verbose_name_plural = "DHIS2 API Credentials"
        ordering = ("api_url",)

    api_url = models.URLField(validators=[validate_dhis2_base_url])
    username = EncryptedTextField()
    password = EncryptedTextField()

    @property
    def display_name(self):
        return self.api_url

    def clean(self):
        try:
            client = Dhis2Client(
                url=self.api_url,
                username=self.username,
                password=self.password,
            )
        except ClientException as e:
            raise ValidationError(f"DHIS2 URL is invalid: {e}")
        try:
            client.fetch_info()
        except RequestException as e:
            if e.code == 401:
                raise ValidationError(
                    "DHIS2 Credentials are invalid, please check username and password"
                )
            if e.code == 500:
                raise ValidationError("DHIS2 URL is invalid")


class InstanceQuerySet(CatalogQuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            instancepermission__team__in=[t.pk for t in user.team_set.all()]
        ).distinct()


class Instance(Datasource):
    def get_permission_set(self):
        return self.instancepermission_set.all()

    class Meta:
        verbose_name = "DHIS2 Instance"
        ordering = ("url",)

    api_credentials = models.ForeignKey(
        "Credentials", null=True, on_delete=models.SET_NULL
    )
    url = models.URLField(blank=True)
    indexes = GenericRelation("catalog.Index")
    name = models.TextField(blank=True)
    locale = LocaleField(default="en")
    verbose_sync = models.BooleanField(default=False)

    objects = InstanceQuerySet.as_manager()

    searchable = True  # TODO: remove (see comment in datasource_index command)

    @property
    def display_name(self):
        return self.name if self.name != "" else self.url

    def __str__(self):
        return self.display_name

    def sync_log(self, fmt, *args):
        if self.verbose_sync:
            logger.info("sync_log %s: " + fmt, self.name, *args)

    def get_pipeline_credentials(self):
        return {
            "name": self.name,
            "url": self.api_credentials.api_url,
            "username": self.api_credentials.username,
            "password": self.api_credentials.password,
        }

    def sync(self):
        """Sync the datasource by querying the DHIS2 API"""
        self.sync_log("start syncing")

        client = Dhis2Client(
            url=self.api_credentials.api_url,
            username=self.api_credentials.username,
            password=self.api_credentials.password,
            verbose=self.verbose_sync,
        )

        self.sync_log("client initialized")
        results = DatasourceSyncResult(datasource=self)

        # Sync data elements
        with transaction.atomic():
            self.last_synced_at = timezone.now()
            info = client.fetch_info()
            self.sync_log("fetch info done: %s", info)
            self.name = info["systemName"]

            self.sync_log("start fetch data_elements")
            for results_batch in client.fetch_data_elements():
                results += sync_from_dhis2_results(
                    model_class=DataElement,
                    instance=self,
                    results=results_batch,
                )

            # Sync indicator types
            self.sync_log("start fetch indicator_types")
            for results_batch in client.fetch_indicator_types():
                results += sync_from_dhis2_results(
                    model_class=IndicatorType,
                    instance=self,
                    results=results_batch,
                )

            # Sync indicators
            self.sync_log("start fetch indicators")
            for results_batch in client.fetch_indicators():
                results += sync_from_dhis2_results(
                    model_class=Indicator,
                    instance=self,
                    results=results_batch,
                )

            # Sync datasets
            self.sync_log("start fetch datasets")
            for results_batch in client.fetch_datasets():
                results += sync_from_dhis2_results(
                    model_class=DataSet,
                    instance=self,
                    results=results_batch,
                )

            # Sync organisation units
            self.sync_log("start fetch organisation_units")
            for results_batch in client.fetch_organisation_units():
                results += sync_from_dhis2_results(
                    model_class=OrganisationUnit,
                    instance=self,
                    results=results_batch,
                )

            # Flag the datasource as synced
            self.sync_log("end of fetching resources")
            self.save()

        self.sync_log("end of syncing")
        return results

    @property
    def content_summary(self):
        de_count = self.dataelement_set.count()
        i_count = self.indicator_set.count()

        return (
            ""
            if de_count == 0 and i_count == 0
            else _("%(count)d item%(suffix)s")
            % {
                "count": de_count + i_count,
                "suffix": pluralize(de_count + i_count),
            }
        )

    def populate_index(self, index):
        index.external_name = self.name
        index.last_synced_at = self.last_synced_at
        index.content = self.content_summary
        index.path = [self.id.hex]
        index.search = f"{self.name}"
        index.datasource_name = self.name
        index.datasource_id = self.id

    def get_absolute_url(self):
        return reverse(
            "connector_dhis2:instance_detail", kwargs={"instance_id": self.id}
        )


class InstancePermission(Permission):
    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("instance", "team")]

    def index_object(self):
        self.instance.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on instance '{self.instance}'"


class EntryQuerySet(CatalogQuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            instance__in=Instance.objects.filter_for_user(user)
        ).distinct()


class Dhis2Entry(Entry):
    class Meta:
        abstract = True

    instance = models.ForeignKey("Instance", null=False, on_delete=models.CASCADE)
    dhis2_id = models.CharField(max_length=200)
    name = models.TextField()
    short_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    external_access = models.BooleanField()
    favorite = models.BooleanField()
    created = models.DateTimeField()
    last_updated = models.DateTimeField()

    objects = EntryQuerySet.as_manager()

    @property
    def display_name(self):
        return self.name

    def update(self, **kwargs):
        for key in {"name", "short_name", "description"} & set(kwargs.keys()):
            setattr(self, key, kwargs[key])

        self.save()


class DomainType(models.TextChoices):
    AGGREGATE = "AGGREGATE", _("Aggregate")
    TRACKER = "TRACKER", _("Tracker")


class ValueType(models.TextChoices):
    TEXT = "TEXT", _("Text")
    LONG_TEXT = "LONG_TEXT", _("Long text")
    LETTER = "LETTER", _("Letter")
    PHONE_NUMBER = "PHONE_NUMBER", _("Phone number")
    EMAIL = "EMAIL", _("Email")
    YES_NO = "YES_NO", _("Yes/No")
    YES_ONLY = "YES_ONLY", _("Yes Only")
    DATE = "DATE", _("Date")
    DATE_AND_TIME = "DATE_AND_TIME", _("Date & Time")
    TIME = "TIME", _("Time")
    NUMBER = "NUMBER", _("Number")
    UNIT_INTERVAL = "UNIT_INTERVAL", _("Unit interval")
    PERCENTAGE = "PERCENTAGE", _("Percentage")
    INTEGER = "INTEGER", _("Integer")
    INTEGER_POSITIVE = "INTEGER_POSITIVE", _("Positive Integer")
    INTEGER_NEGATIVE = "INTEGER_NEGATIVE", _("Negative Integer")
    INTEGER_ZERO_OR_POSITIVE = "INTEGER_ZERO_OR_POSITIVE", _("Positive or Zero Integer")
    TRACKER_ASSOCIATE = "TRACKER_ASSOCIATE", _("Tracker Associate")
    USERNAME = "USERNAME", _("Username")
    COORDINATE = "COORDINATE", _("Coordinate")
    ORGANISATION_UNIT = "ORGANISATION_UNIT", _("Organisation Unit")
    AGE = "AGE", _("Age")
    URL = "URL", _("URL")
    FILE = "FILE", _("File")
    IMAGE = "IMAGE", _("Image")


class AggregationType(models.TextChoices):
    AVERAGE = "AVERAGE", _("Average")
    AVERAGE_SUM_ORG_UNIT = "AVERAGE_SUM_ORG_UNIT ", _("Average sum for org unit")
    COUNT = "COUNT", _("Count")
    CUSTOM = "CUSTOM", _("Custom")
    DEFAULT = "DEFAULT", _("Default")
    LAST = "LAST", _("Last")
    LAST_AVERAGE_ORG_UNIT = "LAST_AVERAGE_ORG_UNIT", _("Last average for org unit")
    MAX = "MAX", _("Max")
    MIN = "MIN", _("Min")
    NONE = "NONE", _("None")
    STDDEV = "STDDEV", _("Standard Deviation")
    SUM = "SUM", _("Sum")
    VARIANCE = "VARIANCE", _("Variance")


class DataElement(Dhis2Entry):
    def get_permission_set(self):
        return self.instance.instancepermission_set.all()

    class Meta:
        verbose_name = "DHIS2 Data Element"
        ordering = ("name",)

    searchable = True  # TODO: remove (see comment in datasource_index command)

    code = models.CharField(max_length=100, blank=True)
    domain_type = models.CharField(choices=DomainType.choices, max_length=100)
    value_type = models.CharField(choices=ValueType.choices, max_length=100)
    aggregation_type = models.CharField(choices=AggregationType.choices, max_length=100)

    def populate_index(self, index):
        index.last_synced_at = self.instance.last_synced_at
        index.external_name = self.name
        index.external_description = self.description
        index.path = [self.instance.id.hex, self.id.hex]
        index.search = f"{self.name} {self.description} {self.dhis2_id}"
        index.datasource_name = self.instance.name
        index.datasource_id = self.instance.id

    def get_absolute_url(self):
        return reverse(
            "connector_dhis2:data_element_detail",
            kwargs={"instance_id": self.instance.id, "data_element_id": self.id},
        )


class OrganisationUnitQuerySet(EntryQuerySet):
    def direct_children_of(
        self, organisation: "OrganisationUnit"
    ) -> QuerySet["OrganisationUnit", "OrganisationUnit"]:
        return self.filter(path__match=str(organisation.path) + ".*{1}")

    def ancestors_of(
        self, organisation: "OrganisationUnit"
    ) -> QuerySet["OrganisationUnit", "OrganisationUnit"]:
        return self.filter(path__ancestors=organisation.path)


class OrganisationUnit(Dhis2Entry):
    def get_permission_set(self):
        return self.instance.instancepermission_set.all()

    class Meta:
        verbose_name = "DHIS2 Organisation Unit"
        ordering = ("name",)

    searchable = True  # TODO: remove (see comment in datasource_index command)

    code = models.CharField(max_length=100, blank=True)
    path = PathField()
    leaf = models.BooleanField()
    datasets = models.ManyToManyField("DataSet", blank=True)

    objects = OrganisationUnitQuerySet.as_manager()

    def populate_index(self, index):
        index.last_synced_at = self.instance.last_synced_at
        index.external_name = self.name
        index.external_description = self.description
        index.path = [self.instance.id.hex, self.id.hex]
        index.search = f"{self.name} {self.description} {self.dhis2_id}"
        index.datasource_name = self.instance.name
        index.datasource_id = self.instance.id

    def get_absolute_url(self):
        return reverse(
            "connector_dhis2:organisation_unit_detail",
            kwargs={"instance_id": self.instance.id, "organisation_unit_id": self.id},
        )


class IndicatorType(Dhis2Entry):
    class Meta:
        verbose_name = "DHIS2 Indicator type"
        ordering = ("name",)

    number = models.BooleanField()
    factor = models.IntegerField()

    def build_index(self):  # TODO: fishy
        pass


class Indicator(Dhis2Entry):
    def get_permission_set(self):
        return self.instance.instancepermission_set.all()

    class Meta:
        verbose_name = "DHIS2 Indicator"
        ordering = ("name",)

    searchable = True  # TODO: remove (see comment in datasource_index command)

    code = models.CharField(max_length=100, blank=True)
    indicator_type = models.ForeignKey(
        "IndicatorType", null=True, on_delete=models.SET_NULL
    )
    annualized = models.BooleanField()

    def populate_index(self, index):
        index.last_synced_at = self.instance.last_synced_at
        index.external_name = self.name
        index.external_description = self.description
        index.path = [self.instance.id.hex, self.id.hex]
        index.search = f"{self.name} {self.description} {self.dhis2_id}"
        index.datasource_name = self.instance.name
        index.datasource_id = self.instance.id

    def get_absolute_url(self):
        return reverse(
            "connector_dhis2:indicator_detail",
            kwargs={"instance_id": self.instance.id, "indicator_id": self.id},
        )


class ExtractStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    REQUESTED = "REQUESTED", _("Requested")
    SUCCESS = "SUCCESS", _("Success")
    FAILED = "FAILED", _("Failed")


class DataSet(Dhis2Entry):
    searchable = True  # TODO: remove (see comment in datasource_index command)

    code = models.CharField(max_length=100, blank=True)
    data_elements = models.ManyToManyField(DataElement, blank=True)

    class Meta:
        verbose_name = "DHIS2 Data Set"
        ordering = ("name",)

    def get_permission_set(self):
        return self.instance.instancepermission_set.all()

    def populate_index(self, index):
        index.last_synced_at = self.instance.last_synced_at
        index.external_name = self.name
        index.external_description = self.description
        index.path = [self.instance.id.hex, self.id.hex]
        index.search = f"{self.name} {self.description} {self.dhis2_id}"
        index.datasource_name = self.instance.name
        index.datasource_id = self.instance.id

    def get_absolute_url(self):
        return reverse(
            "connector_dhis2:dataset_detail",
            kwargs={"instance_id": self.instance.id, "dataset_id": self.id},
        )


class ExtractQuerySet(CatalogQuerySet):
    def filter_for_user(self, user):
        return self.filter(user=user)


class Extract(Base):
    data_elements = models.ManyToManyField("DataElement")
    indicators = models.ManyToManyField("Indicator")
    period = models.CharField(max_length=200)
    status = models.CharField(max_length=100, choices=ExtractStatus.choices)
    user = models.ForeignKey("user_management.User", on_delete=models.CASCADE)

    objects = ExtractQuerySet.as_manager()

    @property
    def display_name(self):
        return f"{_('Extract')} {date_format(self.created_at)}"
