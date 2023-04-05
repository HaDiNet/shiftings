from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Any

from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.cal.views.calendar_base import CalendarBaseView
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.models import Shift, ShiftType


class DayView(CalendarBaseView, ABC):
    template_name = 'cal/day_calendar.html'
    save_path_in_session = True
    url_name_suffix = ''

    def get_title(self) -> str:
        if 'theday' in self.kwargs:
            return _('Day {date}').format(date=self.kwargs.get('theday'))
        return _('Day Overview')

    @abstractmethod
    def get_shifts(self, theday: date) -> Any:
        raise NotImplementedError('get_shifts needs to be implemented')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        theday = date.fromisoformat(self.kwargs.get('theday')) if 'theday' in self.kwargs else date.today()
        context.update({
            'theday': theday,
            'next_url': reverse('overview_day' + self.url_name_suffix, args=[theday + timedelta(days=1)]),
            'prev_url': reverse('overview_day' + self.url_name_suffix, args=[theday - timedelta(days=1)]),
            'today_url': reverse('overview_today' + self.url_name_suffix),
            'day_hours': list(range(24)),
            'shifts': self.get_shifts(theday),
            'add_self_form': AddSelfParticipantForm(self.object, initial={'user': self.request.user}),
        })
        return context


class DetailDayView(DayView):
    extra_context = {
        'day_calendar_template': 'cal/template/day_calendar_xs.html'
    }

    def get_shifts(self, theday: date) -> Any:
        shift_filter = (Q(start__date=theday) | Q(end__date=theday, end__gt=theday) |
                        Q(start__lt=theday, end__gt=theday))
        shift_filter &= self.get_filters()
        shifts = Shift.objects.filter(shift_filter).order_by('start', 'end', 'shift_type')
        return [shift for shift in shifts if shift.can_see(self.request.user)]


class ShiftTypesDayView(DayView):
    extra_context = {
        'day_calendar_template': 'cal/template/day_calendar_shift_types.html'
    }
    url_name_suffix = '_shift_types'

    def get_shifts(self, theday: date):
        shift_filter = Q(start__date=theday) & self.get_filters()
        shifts = Shift.objects.filter(shift_filter).order_by('start', 'shift_type')
        shifts = [shift for shift in shifts if shift.can_see(self.request.user)]
        types = ShiftType.objects.filter(shift__in=shifts).distinct()
        shift_idx_type = {
            'types': types,
            'time_containers': {}
        }
        for shift in shifts:
            if shift.can_see(self.request.user):
                shift_idx_type['time_containers'].setdefault(shift.start.hour, {}).setdefault(shift.shift_type.name, []).append(
                    shift
                )
        return shift_idx_type
