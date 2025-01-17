from enum import Enum
from typing import Dict, List, Tuple

import psycopg2
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from psycopg2 import OperationalError, sql

from hexa.catalog.models import CatalogQuerySet, Datasource, Entry
from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models import Permission
from hexa.core.models.cryptography import EncryptedTextField


class ExternalType(Enum):
    DATABASE = "database"
    TABLE = "table"


class DatabaseQuerySet(CatalogQuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(
            databasepermission__team__in=[t.pk for t in user.team_set.all()]
        ).distinct()


class Database(Datasource):
    def get_permission_set(self):
        return self.databasepermission_set.all()

    searchable = True  # TODO: remove (see comment in datasource_index command)

    hostname = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = EncryptedTextField(max_length=200)
    port = models.IntegerField(default=5432)
    database = models.CharField(max_length=200)

    postfix = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "PostgreSQL Database"
        ordering = ("hostname",)
        unique_together = [("database", "postfix")]

    objects = DatabaseQuerySet.as_manager()

    @property
    def unique_name(self):
        if self.postfix:
            return f"{self.database}{self.postfix}"
        else:
            return self.database

    @property
    def env_name(self):
        slug = self.unique_name.replace("-", "_").upper()
        return f"POSTGRESQL_{slug}"

    @property
    def url(self):
        return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"

    @property
    def safe_url(self):
        return (
            f"postgresql://{self.username}@{self.hostname}:{self.port}/{self.database}"
        )

    @property
    def content_summary(self):
        count = self.table_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d table%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    def get_pipeline_credentials(self):
        return {
            "hostname": self.hostname,
            "username": self.username,
            "password": self.password,
            "port": self.port,
            "database": self.database,
        }

    def populate_index(self, index):
        index.last_synced_at = self.last_synced_at
        index.external_name = self.database
        index.external_id = self.safe_url
        index.external_type = ExternalType.DATABASE.value
        index.search = f"{self.database}"
        index.path = [self.id.hex]
        index.content = self.content_summary
        index.datasource_name = self.database
        index.datasource_id = self.id

    @property
    def display_name(self):
        return self.unique_name

    def __str__(self):
        return self.display_name

    def clean(self):
        try:
            with psycopg2.connect(self.url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 = 1")
                    cursor.fetchall()
        except OperationalError as e:
            if "could not connect to server" in str(e):
                raise ValidationError(
                    "Could not connect to server, please check hostname and port"
                )
            elif str(e).startswith("FATAL: "):
                err = str(e).removeprefix("FATAL: ")
                raise ValidationError(err)
            else:
                raise ValidationError(e)

    def sync(self):
        created_count = 0
        updated_count = 0
        identical_count = 0
        deleted_count = 0

        # Ignore tables from postgis as there is no value in showing them in the catalog
        IGNORE_TABLES = ["geography_columns", "geometry_columns", "spatial_ref_sys"]

        with psycopg2.connect(self.url) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT table_name, table_type, pg_class.reltuples as row_count
                    FROM information_schema.tables
                    JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """
                )
                response: List[Tuple[str, str, int]] = cursor.fetchall()

                new_tables: Dict[str, Dict] = {
                    x[0]: x for x in response if x[0] not in IGNORE_TABLES
                }

                for name, data in new_tables.items():
                    if data["row_count"] < 10_000:
                        cursor.execute(
                            sql.SQL("SELECT COUNT(*) as row_count FROM {};").format(
                                sql.Identifier(data["table_name"])
                            ),
                        )
                        response = cursor.fetchone()
                        new_tables[name]["row_count"] = response["row_count"]

        with transaction.atomic():
            existing_tables = Table.objects.filter(database=self)
            for table in existing_tables:
                if table.name not in new_tables.keys():
                    deleted_count += 1
                    table.delete()
                else:
                    data = new_tables[table.name]
                    if table.rows == data["row_count"]:
                        identical_count += 1
                    else:
                        table.rows = data["row_count"]
                        updated_count += 1
                    table.save()

            for new_table_name, new_table in new_tables.items():
                if new_table_name not in {x.name for x in existing_tables}:
                    created_count += 1
                    Table.objects.create(
                        name=new_table_name, database=self, rows=data["row_count"]
                    )

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            deleted=deleted_count,
        )

    def get_absolute_url(self):
        return reverse(
            "connector_postgresql:datasource_detail", kwargs={"datasource_id": self.id}
        )


class TableQuerySet(CatalogQuerySet):
    def filter_for_user(self, user):
        if user.is_active and user.is_superuser:
            return self

        return self.filter(database__in=Database.objects.filter_for_user(user))


class Table(Entry):
    database = models.ForeignKey("Database", on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    rows = models.IntegerField(default=0)

    searchable = True  # TODO: remove (see comment in datasource_index command)

    class Meta:
        verbose_name = "PostgreSQL table"
        ordering = ["name"]

    objects = TableQuerySet.as_manager()

    def get_permission_set(self):
        return self.database.databasepermission_set.all()

    def populate_index(self, index):
        index.last_synced_at = self.database.last_synced_at
        index.external_name = self.name
        index.external_type = ExternalType.TABLE.value
        index.path = [self.database.id.hex, self.id.hex]
        index.external_id = f"{self.database.safe_url}/{self.name}"
        index.context = self.database.database
        index.search = f"{self.name}"
        index.datasource_name = self.database.database
        index.datasource_id = self.database.id

    def get_absolute_url(self):
        return reverse(
            "connector_postgresql:table_detail",
            kwargs={"datasource_id": self.database.id, "table_id": self.id},
        )


class DatabasePermission(Permission):
    database = models.ForeignKey(
        "connector_postgresql.Database", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [("database", "team")]

    def index_object(self):
        self.database.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on database '{self.database}'"
