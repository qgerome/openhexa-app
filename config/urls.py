"""hexa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from ariadne.contrib.django.views import GraphQLView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings

from .schema import schema
from hexa.plugins.app import get_connector_app_configs

# Core URLs
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hexa.core.urls", namespace="core")),
    path("user/", include("hexa.user_management.urls", namespace="user")),
    path("catalog/", include("hexa.catalog.urls", namespace="catalog")),
    path("notebooks/", include("hexa.notebooks.urls", namespace="notebooks")),
    path("pipelines/", include("hexa.pipelines.urls", namespace="pipelines")),
    path("comments/", include("hexa.comments.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        "graphql/",
        GraphQLView.as_view(
            schema=schema, playground_options={"request.credentials": "include"}
        )
        if settings.DEBUG is True
        else TemplateView.as_view(template_name="404.html"),
        name="graphql",
    ),
]

# Connector apps URLs
for app_config in get_connector_app_configs():
    urlpatterns.append(
        path(
            app_config.route_prefix + "/",
            include(app_config.name + ".urls", namespace=app_config.label),
        )
    )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
