from django.apps import apps

from habari.plugins.app import ConnectorAppConfig


def get_connector_app_configs():
    """Return the list of Django app configs that corresponds to connector apps"""

    return [
        app for app in apps.get_app_configs() if isinstance(app, ConnectorAppConfig)
    ]
