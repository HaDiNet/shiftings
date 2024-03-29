from datetime import date
from typing import Any, Optional

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from shiftings.cal.feed.base import ShiftFeed
from shiftings.events.models import Event
from shiftings.shifts.models import Shift
from shiftings.utils.exceptions import Http403


class EventFeed(ShiftFeed[Event]):
    def get_object(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Optional[Event]:
        if not request.user.is_authenticated:
            raise Http403()
        event: Event = Event.objects.get(pk=kwargs['pk'])
        if not event.can_see(request.user):
            raise Http403()
        return event

    def file_name(self, obj: Event) -> str:
        return f'event_{obj.display.lower().replace(" ", "_")}_shifts.ics'

    def title(self, obj: Event) -> str:
        return obj.display

    def description(self, obj: Event) -> str:
        return obj.description

    def items(self, obj: Event) -> QuerySet[Shift]:
        return obj.shifts.filter(end__gte=date.today())


class PublicEventsFeed(ShiftFeed[Event]):
    def get_object(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        return None

    def file_name(self, obj: Event) -> str:
        return f'public_events_shifts.ics'

    def title(self, obj: Event) -> str:
        return _('Public Events')

    def description(self, obj: Event) -> str:
        return obj.description

    def items(self, obj: Event) -> QuerySet[Shift]:
        return Shift.objects.none()
