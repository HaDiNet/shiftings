from datetime import date
from typing import Any, Optional

from django.db.models import QuerySet
from django.http import HttpRequest

from shiftings.cal.feed.base import ShiftFeed
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Shift
from shiftings.utils.exceptions import Http403


class OrganizationFeed(ShiftFeed[Organization]):
    def get_object(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Optional[Organization]:
        if not request.user.is_authenticated:
            raise Http403()
        org: Organization = Organization.objects.get(pk=kwargs['pk'])
        if not org.is_member(request.user):
            raise Http403()
        return org

    def file_name(self, obj: Organization) -> str:
        return f'{obj.display.lower().replace(" ", "_")}_shifts.ics'

    def title(self, obj: Organization) -> str:
        return obj.display

    def items(self, obj: Organization) -> QuerySet[Shift]:
        return obj.shifts.filter(end__gte=date.today())
