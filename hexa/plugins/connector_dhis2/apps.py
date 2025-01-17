from hexa.plugins.app import ConnectorAppConfig


class Dhis2ConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_dhis2"
    label = "connector_dhis2"

    verbose_name = "DHIS2 Connector"

    @property
    def route_prefix(self):
        return "dhis2"
