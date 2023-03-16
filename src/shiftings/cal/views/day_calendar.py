from datetime import date, timedelta
from typing import Any

from django.db.models import Q

from shiftings.cal.views.calendar_base import CalendarBaseView
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.models import Shift


class DayView(CalendarBaseView):
    template_name = 'cal/day_calendar.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        theday = date.fromisoformat(self.kwargs.get('theday')) if 'theday' in self.kwargs else date.today()
        shift_filter = (Q(start__date=theday) | Q(end__date=theday, end__gt=theday) |
                        Q(start__lt=theday, end__gt=theday))
        shift_filter &= self.get_filters()
        shifts = Shift.objects.filter(shift_filter).order_by('start', 'end', 'shift_type')
        context.update({
            'theday': theday,
            'nextday': theday + timedelta(days=1),
            'prevday': theday - timedelta(days=1),
            'day_hours': list(range(24)),
            'shifts': shifts,
            'add_self_form': AddSelfParticipantForm(self.object, initial={'user': self.request.user}),
        })
        return context
