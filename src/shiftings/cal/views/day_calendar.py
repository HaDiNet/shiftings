from datetime import date, timedelta
from typing import Any

from django.db.models import Q

from shiftings.cal.views.calendar_base import CalendarBaseView
from shiftings.shifts.models import Shift


class DayView(CalendarBaseView):
    template_name = 'cal/day_calendar.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        theday = date.fromisoformat(self.kwargs.get('theday')) if 'theday' in self.kwargs else date.today()
        shift_filter = (Q(start__date=theday) | Q(end__date=theday, end__gt=theday) |
                        Q(start__lt=theday, end__gt=theday))
        shift_filter &= self.get_filters()
        shifts = Shift.objects.filter(shift_filter).order_by('shift_type', 'start', 'end')
        context.update({
            'theday': theday,
            'nextday': theday + timedelta(days=1),
            'prevday': theday - timedelta(days=1),
            'day_hours': list(range(24)),
            'shifts': [self.get_shift_day_metadata(theday, shift) for shift in
                       shifts]
        })
        return context

    def get_shift_day_metadata(self, day: date, shift: Shift):
        duration = 24
        if day == shift.end.date():
            end_hour = 24 - shift.end.hour
            duration = shift.end.hour
            if duration == 0:
                duration = 1
                end_hour -= 1
        else:
            end_hour = 0

        if day == shift.start.date():
            start_hour = shift.start.hour
            duration -= start_hour
        else:
            start_hour = 0
        return {
            'shift': shift,
            'start_hour': list(range(start_hour)),
            'duration': duration,
            'end_hour': list(range(end_hour)),
        }
