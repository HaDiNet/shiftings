from datetime import date
from typing import Any, Optional, Union

from django import template
from django.utils.safestring import mark_safe

from shiftings.cal.views.month_summary_calendar import MonthOverviewCalendar
from shiftings.events.models import Event
from shiftings.organizations.models import Organization

register = template.Library()


@register.simple_tag()
def month_overview_calendar(model: Union[Event, Organization], get_data: dict[str, Any],
                            override_date: Optional[date] = None):
    if override_date is None or override_date < date.today():
        current_date = date.today()
    else:
        current_date = override_date

    if isinstance(model, Event) and override_date is None:
        if model.start_date > current_date:
            current_date = model.start_date
        elif model.end_date < current_date:
            current_date = model.end_date


    if 'month' in get_data and 'year' in get_data:
        current_date = date(int(get_data.get('year', current_date.year)),
                            int(get_data.get('month', current_date.month)),
                            1)
    return mark_safe(MonthOverviewCalendar(model).format(current_date or date.today()))
