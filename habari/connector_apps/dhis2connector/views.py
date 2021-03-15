from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from habari.catalog.lists import build_summary_list_params, build_paginated_list_params
from habari.catalog.models import CatalogIndex, CatalogIndexType
from habari.connector_apps.dhis2connector.models import Dhis2Instance


def datasource_detail(request, datasource_id):
    datasource = get_object_or_404(Dhis2Instance, pk=datasource_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "dhis2connector/datasource_detail.html",
        {
            "datasource": datasource,
            "data_elements_list_params": build_summary_list_params(
                datasource.dhis2dataelement_set.all(),
                title=_("Data elements"),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                paginated_list_url="dhis2connector:data_element_list",
                item_name=_("data element"),
                item_template="dhis2connector/partials/data_element_list_item.html",
            ),
            "indicators_list_params": build_summary_list_params(
                datasource.dhis2indicator_set.all(),
                title=_("Indicators"),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                paginated_list_url="dhis2connector:indicator_list",
                item_name=_("indicator"),
                item_template="dhis2connector/partials/indicator_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_list(request, datasource_id):
    datasource = get_object_or_404(Dhis2Instance, pk=datasource_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
        (_("Data Elements"),),
    ]

    return render(
        request,
        "dhis2connector/data_element_list.html",
        {
            "datasource": datasource,
            "data_elements_list_params": build_paginated_list_params(
                datasource.dhis2dataelement_set.all(),
                title=_("Data elements"),
                page_number=int(request.GET.get("page", "1")),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                item_name=_("data element"),
                item_template="dhis2connector/partials/data_element_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_detail(request, datasource_id, data_element_id):
    datasource = get_object_or_404(Dhis2Instance, pk=datasource_id)
    data_element = get_object_or_404(
        datasource.dhis2dataelement_set, pk=data_element_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
        (_("Data Elements"), "dhis2connector:data_element_list", datasource_id),
        (data_element.display_name,),
    ]

    return render(
        request,
        "dhis2connector/data_element_detail.html",
        {
            "datasource": datasource,
            "data_element": data_element,
            "breadcrumbs": breadcrumbs,
        },
    )


def indicator_list(request, datasource_id):
    datasource = get_object_or_404(Dhis2Instance, pk=datasource_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
        (_("Indicators"),),
    ]

    return render(
        request,
        "dhis2connector/indicator_list.html",
        {
            "datasource": datasource,
            "indicators_list_params": build_paginated_list_params(
                datasource.dhis2indicator_set.all(),
                title=_("Indicators"),
                page_number=int(request.GET.get("page", "1")),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                item_name=_("indicator"),
                item_template="dhis2connector/partials/indicator_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def indicator_detail(request, datasource_id, indicator_id):
    datasource = get_object_or_404(Dhis2Instance, pk=datasource_id)
    indicator = get_object_or_404(datasource.dhis2indicator_set, pk=indicator_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (datasource.display_name, "dhis2connector:datasource_detail", datasource_id),
        (_("Indicators"), "dhis2connector:indicator_list", datasource_id),
        (indicator.display_name,),
    ]

    return render(
        request,
        "dhis2connector/indicator_detail.html",
        {
            "datasource": datasource,
            "indicator": indicator,
            "breadcrumbs": breadcrumbs,
        },
    )


def datasource_sync(request, datasource_id):
    datasource = get_object_or_404(Dhis2Instance, pk=datasource_id)
    sync_result = datasource.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
