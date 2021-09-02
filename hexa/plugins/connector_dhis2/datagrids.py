from hexa.plugins.connector_dhis2.models import DataElement, DomainType, Indicator
from hexa.ui.datagrid import (
    Datagrid,
    LeadingColumn,
    TextColumn,
    LinkColumn,
    DateColumn,
)


class DataElementGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="get_value_type_display",
        icon="get_icon",
    )
    code = TextColumn(text="code")
    tags = TextColumn(text="todo_tags")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")

    def get_icon(self, data_element: DataElement):
        if data_element.domain_type == DomainType.AGGREGATE:
            return "ui/icons/chart_bar.html"
        elif data_element.domain_type == DomainType.TRACKER:
            return "ui/icons/user_circle.html"

        return "ui/icons/exclamation.html"


class IndicatorGrid(Datagrid):
    lead = LeadingColumn(
        label="Name",
        text="name",
        secondary_text="indicator_type.name",
    )
    code = TextColumn(text="code")
    tags = TextColumn(text="todo_tags")
    last_synced = DateColumn(date="instance.last_synced_at")
    view = LinkColumn(text="View")