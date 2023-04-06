from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from django.conf import settings
from django.db.models import Model, QuerySet
from django.http import HttpRequest
from django_ical.views import ICalFeed
from icalendar import vCalAddress, vText

from shiftings.shifts.models import Shift

T = TypeVar('T', bound=Model)


class ShiftFeed(ABC, ICalFeed, Generic[T]):
    timezone = settings.TIME_ZONE

    def product_id(self, obj: Optional[T]) -> str:
        if obj:
            return f'-//{settings.PROVIDER}//{self.__class__.__name__}//{obj.pk}//EN'
        return f'-//{settings.PROVIDER}//{self.__class__.__name__}//EN'

    @abstractmethod
    def get_object(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Optional[T]:
        pass

    def file_name(self, obj: T) -> str:
        return 'event.ics'

    @abstractmethod
    def title(self, obj: T) -> str:
        pass

    @abstractmethod
    def description(self, obj: T) -> str:
        pass

    @abstractmethod
    def items(self, obj: T) -> QuerySet[Shift]:
        return Shift.objects.all().order_by('-start')

    def item_title(self, item: Shift) -> str:
        return item.name

    def item_description(self, item: Shift) -> str:
        return item.place

    def item_class(self, item: Shift) -> str:
        return 'PRIVATE'

    def item_created(self, item: Shift) -> datetime:
        return item.created

    def item_item_updateddate(self, item: Shift) -> datetime:
        return item.modified

    def item_start_datetime(self, item: Shift) -> datetime:
        return item.start

    def item_end_datetime(self, item: Shift) -> datetime:
        return item.end

    def item_location(self, item: Shift) -> str:
        return item.place

    def item_organizer(self, item: Shift) -> Optional[vCalAddress]:
        if item.email:
            organizer = vCalAddress(f'MAILTO:{item.email}')
            organizer.params['cn'] = vText(item.organization.name)
            organizer.params['ROLE'] = vText('CHAIR')
            return organizer
        return None

    def item_attendee(self, item: Shift) -> list[vCalAddress]:
        attendees = list()
        for participant in item.participants.all():
            if participant.user.email:
                attendee = vCalAddress(f'MAILTO:{participant.user.email}')
                attendee.params['cn'] = participant.display
                attendee.params['PARTSTAT'] = 'ACCEPTED'
                attendees.append(attendee)
        return attendees

    # def item_valarm(self, item: Shift) -> list[Alarm]:
    #     alarm = Alarm()
    #     alarm.add('action', 'DISPLAY')
    #     alarm.add('trigger', timedelta(minutes=-30))
    #     alarm.add('description', _('Shift Reminder'))
    #     return [alarm]
