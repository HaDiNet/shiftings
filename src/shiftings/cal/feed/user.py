from typing import Any, Optional

from django.db.models import Q, QuerySet
from django.http import HttpRequest

from shiftings.accounts.models import User
from shiftings.cal.feed.base import ShiftFeed
from shiftings.shifts.models import Shift
from shiftings.utils.exceptions import Http403


class UserFeed(ShiftFeed[User]):
    def get_object(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Optional[User]:
        if request.user.is_authenticated:
            return request.user

        # noinspection all
        user = User.objects.get(ical_token=request.GET.get('token', ''))
        return user

    def file_name(self, obj: User) -> str:
        return f'{obj.display.lower().replace(" ", "_")}_shifts.ics'

    def title(self, obj: User) -> str:
        return obj.display

    def description(self, obj: User) -> str:
        return ''

    def items(self, obj: User) -> QuerySet[Shift]:
        organizations = obj.organizations
        query = Q(organization__in=organizations)
        query |= Q(event__organization__in=organizations)
        query |= Q(participants__user=obj)
        return Shift.objects.filter(query).distinct()


class OwnShiftsFeed(UserFeed):
    def file_name(self, obj: User) -> str:
        return f'my_{super().file_name(obj)}'

    def items(self, obj: User) -> QuerySet[Shift]:
        return Shift.objects.filter(participants__user=obj).distinct()
