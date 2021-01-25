from dhis2 import Api
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import Base, Content
from .common import DatasourceType


class SyncResult:
    def __init__(self, datasource, created, updated, identical):
        self.datasource = datasource
        self.created = created
        self.updated = updated
        self.identical = identical

    def __str__(self):
        figures = (
            f"{self.created} new, {self.updated} updated, {self.identical} unaffected"
        )

        return f'The datasource "{self.datasource.display_name}" has been synced ({figures})'

    def __add__(self, other):
        if other.datasource != self.datasource:
            raise ValueError(
                "The two SyncResults instances don't have the same datasource"
            )

        return SyncResult(
            datasource=self.datasource,
            created=self.created + other.created,
            updated=self.updated + other.updated,
            identical=self.identical + other.identical,
        )


class ContentSummary:
    def __init__(self, data_element_count, data_indicator_count):
        self.data_element_count = data_element_count
        self.data_indicator_count = data_indicator_count
        self.total_count = self.data_element_count + self.data_indicator_count

    def __str__(self):
        return f"{self.data_element_count} data element(s), {self.data_indicator_count} data indicator(s)"


class Dhis2Connection(Base):
    source = models.OneToOneField(
        "Datasource", on_delete=models.CASCADE, related_name="connection"
    )
    api_url = models.URLField()
    api_username = models.CharField(max_length=200)
    api_password = models.CharField(max_length=200)

    def sync(self):
        """Sync the datasource by querying the DHIS2 API"""

        dhis2 = Api(self.api_url, self.api_username, self.api_password)

        # Sync DE
        de_response = dhis2.get_paged(
            "dataElements", params={"fields": ":all"}, page_size=100, merge=True
        )
        de_result = Dhis2DataElement.objects.sync_from_dhis2_api_response(
            self.source, de_response
        )

        # Sync DI
        di_response = dhis2.get_paged(
            "indicators", params={"fields": ":all"}, page_size=100, merge=True
        )
        di_result = Dhis2Indicator.objects.sync_from_dhis2_api_response(
            self.source, di_response
        )

        return de_result + di_result

    def get_content_summary(self):
        return ContentSummary(
            data_element_count=self.source.dhis2dataelement_set.count(),
            data_indicator_count=0,
        )


class Dhis2Area(Content):
    pass


class Dhis2Theme(Content):
    pass


class Dhis2Data(Content):
    class Meta:
        abstract = True
        ordering = ["name"]

    owner = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    source = models.ForeignKey(
        "Datasource",
        on_delete=models.CASCADE,
        limit_choices_to={"source_type": DatasourceType.DHIS2.value},
    )
    area = models.ForeignKey(
        "Dhis2Area", null=True, blank=True, on_delete=models.SET_NULL
    )
    theme = models.ForeignKey(
        "Dhis2Theme", null=True, blank=True, on_delete=models.SET_NULL
    )
    dhis2_id = models.CharField(max_length=100, unique=True)
    dhis2_code = models.CharField(max_length=100, blank=True)


class Dhis2DomainType(models.TextChoices):
    AGGREGATE = "AGGREGATE", _("Aggregate")
    TRACKER = "TRACKER", _("Tracker")


class Dhis2ValueType(models.TextChoices):
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
    # TODO: check order of the next 6 items
    POSITIVE_INTEGER = "POSITIVE_INTEGER", _("Positive Integer")
    INTEGER_POSITIVE = "INTEGER_POSITIVE", _("Positive Integer")
    NEGATIVE_INTEGER = "NEGATIVE_INTEGER", _("Negative Integer")
    INTEGER_NEGATIVE = "INTEGER_NEGATIVE", _("Negative Integer")
    POSITIVE_OR_ZERO_INTEGER = "POSITIVE_OR_ZERO_INTEGER", _("Positive or Zero Integer")
    INTEGER_ZERO_OR_POSITIVE = "INTEGER_ZERO_OR_POSITIVE", _("Positive or Zero Integer")
    TRACKER_ASSOCIATE = "TRACKER_ASSOCIATE", _("Tracker Associate")
    USERNAME = "USERNAME", _("Username")
    COORDINATE = "COORDINATE", _("Coordinate")
    ORGANISATION_UNIT = "ORGANISATION_UNIT", _("Organisation Unit")
    AGE = "AGE", _("Age")
    URL = "URL", _("URL")
    FILE = "FILE", _("File")
    IMAGE = "IMAGE", _("Image")


class Dhis2AggregationType(models.TextChoices):
    SUM = "SUM", _("Sum")
    AVERAGE = "AVERAGE", _("Average")
    # TODO: complete


class Dhis2DataElementQuerySet(models.QuerySet):
    FIELD_MAPPINGS = {
        "dhis2_id": "id",
        "dhis2_code": "code",
        "name": "name",
        "short_name": "shortName",
        "dhis2_domain_type": "domainType",
        "dhis2_value_type": "valueType",
        "dhis2_aggregation_type": "aggregationType",
    }

    def sync_from_dhis2_api_response(self, datasource, response):
        """Iterate over the DEs in the response and create, update or ignore depending on local data
        :todo: refactor - a lot of duplicated code with Dhis2IndicatorQueryset
        """

        created = 0
        updated = 0
        identical = 0

        de_list = response["dataElements"]
        for de_data in de_list:
            try:
                description = next(
                    p
                    for p in de_data["translations"]
                    if p["property"] == "DESCRIPTION" and "en_" in p["locale"]
                )["value"]
            except StopIteration:
                try:
                    description = next(
                        p
                        for p in de_data["translations"]
                        if p["property"] == "DESCRIPTION"
                    )["value"]
                except StopIteration:
                    description = ""

            field_values = {"description": description} | {
                field_name: de_data.get(dhis2_key, "")
                for field_name, dhis2_key in self.FIELD_MAPPINGS.items()
            }

            try:
                # Check if the DE is already in our database and compare values (local vs dhis2)
                existing_de = self.get(dhis2_id=de_data["id"])
                existing_field_values = {
                    field_name: getattr(existing_de, field_name)
                    for field_name, dhis2_key in self.FIELD_MAPPINGS.items()
                }
                diff_field_values = {
                    field_name: field_values[field_name]
                    for field_name in self.FIELD_MAPPINGS.keys()
                    if field_values[field_name] != existing_field_values[field_name]
                }

                # Check if we need to actually update the local version
                if len(diff_field_values) > 0:
                    for field_name in diff_field_values:
                        setattr(existing_de, field_name, diff_field_values[field_name])
                    updated += 1
                else:
                    identical += 1
            # If we don't have the DE locally, create it
            except Dhis2DataElement.DoesNotExist:
                super().create(**field_values, source=datasource)
                created += 1

        return SyncResult(
            datasource=datasource, created=created, updated=updated, identical=identical
        )


class Dhis2DataElement(Dhis2Data):
    dhis2_domain_type = models.CharField(
        choices=Dhis2DomainType.choices, max_length=100
    )
    dhis2_value_type = models.CharField(choices=Dhis2ValueType.choices, max_length=100)
    dhis2_aggregation_type = models.CharField(
        choices=Dhis2AggregationType.choices, max_length=100
    )

    objects = Dhis2DataElementQuerySet.as_manager()

    @property
    def dhis2_domain_type_label(self):
        try:
            return Dhis2DomainType[self.dhis2_domain_type].label
        except KeyError:
            return "Unknown"

    @property
    def dhis2_value_type_label(self):
        try:
            return Dhis2ValueType[self.dhis2_value_type].label
        except KeyError:
            return "Unknown"

    @property
    def dhis2_aggregation_type_label(self):
        try:
            return Dhis2AggregationType[self.dhis2_aggregation_type].label
        except KeyError:
            return "Unknown"


class Dhis2IndicatorType(models.TextChoices):
    NUMBER_FACTOR_1 = "NUMBER_FACTOR_1", _("Number (Factor 1)")
    PER_CENT = "PER_CENT", _("Per cent")
    PER_HUNDRED_THOUSANDS = "PER_HUNDRED_THOUSANDS", _("Per hundred thousand")
    PER_TEN_THOUSAND = "PER_TEN_THOUSAND", _("Per ten thousand")
    PER_THOUSAND = "PER_THOUSAND", _("Per thousand")


class Dhis2IndicatorQuerySet(models.QuerySet):
    FIELD_MAPPINGS = {
        "dhis2_id": "id",
        "dhis2_code": "code",
        "name": "name",
        "short_name": "shortName",
        "annualized": "annualized",
        # TODO: check
        # "dhis2_indicator_type": "indicatorType",
    }

    def sync_from_dhis2_api_response(self, datasource, response):
        """Iterate over the DIs in the response and create, update or ignore depending on local data
        :todo: refactor - a lot of duplicated code with Dhis2DataElementQueryset
        """

        created = 0
        updated = 0
        identical = 0

        di_list = response["indicators"]
        for di_data in di_list:
            try:
                description = next(
                    p
                    for p in di_data["translations"]
                    if p["property"] == "DESCRIPTION" and "en_" in p["locale"]
                )["value"]
            except StopIteration:
                try:
                    description = next(
                        p
                        for p in di_data["translations"]
                        if p["property"] == "DESCRIPTION"
                    )["value"]
                except StopIteration:
                    description = ""

            field_values = {
                "description": description,
                "dhis2_indicator_type": Dhis2IndicatorType.PER_CENT,
            } | {
                field_name: di_data.get(dhis2_key, "")
                for field_name, dhis2_key in self.FIELD_MAPPINGS.items()
            }

            try:
                # Check if the DE is already in our database and compare values (local vs dhis2)
                existing_di = self.get(dhis2_id=di_data["id"])
                existing_field_values = {
                    field_name: getattr(existing_di, field_name)
                    for field_name, dhis2_key in self.FIELD_MAPPINGS.items()
                }
                diff_field_values = {
                    field_name: field_values[field_name]
                    for field_name in self.FIELD_MAPPINGS.keys()
                    if field_values[field_name] != existing_field_values[field_name]
                }

                # Check if we need to actually update the local version
                if len(diff_field_values) > 0:
                    for field_name in diff_field_values:
                        setattr(existing_di, field_name, diff_field_values[field_name])
                    updated += 1
                else:
                    identical += 1
            # If we don't have the DE locally, create it
            except Dhis2Indicator.DoesNotExist:
                super().create(**field_values, source=datasource)
                created += 1

        return SyncResult(
            datasource=datasource, created=created, updated=updated, identical=identical
        )


class Dhis2Indicator(Dhis2Data):
    dhis2_indicator_type = models.CharField(
        choices=Dhis2IndicatorType.choices, max_length=100
    )
    annualized = models.BooleanField()

    objects = Dhis2IndicatorQuerySet.as_manager()

    @property
    def dhis2_indicator_type_label(self):
        try:
            return Dhis2IndicatorType[self.dhis2_indicator_type].label
        except KeyError:
            return "Unknown"