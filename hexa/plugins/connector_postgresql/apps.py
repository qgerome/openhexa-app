from hexa.plugins.app import ConnectorAppConfig


class PostgresqlConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_postgresql"
    label = "connector_postgresql"

    verbose_name = "Postgresql Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_postgresql.credentials.notebooks_credentials"
    ]

    @property
    def route_prefix(self):
        return "postgresql"
