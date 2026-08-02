from datetime import date
from typing import Any, Optional

from django.db.models import QuerySet
from django.http import HttpRequest

from shiftings.cal.feed.base import ShiftFeed
from shiftings.cal.feed.helpers import FeedAccessMixin
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Shift


class OrganizationFeed(FeedAccessMixin, ShiftFeed[Organization]):
    def get_object(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Optional[Organization]:
        self.ensure_authenticated(request)
        org: Organization = Organization.objects.get(pk=kwargs['pk'])
        self.ensure_org_member_or_admin(org, request.user)
        return org

    def file_name(self, obj: Organization) -> str:
        return f'{obj.display.lower().replace(" ", "_")}_shifts.ics'

    def title(self, obj: Organization) -> str:
        return obj.display

    def description(self, obj: Organization) -> str:
        return obj.description

    def items(self, obj: Organization) -> QuerySet[Shift]:
        return obj.shifts.filter(end__gte=date.today())
