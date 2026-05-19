from django.contrib import admin

from shiftings.events.models import Event
from shiftings.utils.admin import BaseModelAdmin, RelatedObjectsFilter
from shiftings.organizations.models import Organization


class OrganizationWithEventsFilter(RelatedObjectsFilter):
    title = 'Organization'
    parameter_name = 'organization'
    related_model = Organization
    related_model_filter = {'events__isnull': False}
    queryset_filter_field = 'organization'

@admin.register(Event)
class EventAdmin(BaseModelAdmin):
    search_fields = (
        'name',
        'organization__name',
        'email',
        'website',
        'description',
    )
    list_filter = (
        OrganizationWithEventsFilter,
        'start_date',
    )
