from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Any

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from shiftings.cal.forms.day_form import SelectDayForm
from shiftings.cal.views.calendar_base import CalendarBaseView
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.models import Shift, ShiftType


class ListView(CalendarBaseView, ABC):
    template_name = 'cal/list_calendar.html'
    save_path_in_session = True
    url_name_suffix = ''

    def get_title(self) -> str:
        return _('Shift Overview')

    @abstractmethod
    def get_shifts(self) -> Any:
        raise NotImplementedError('get_shifts needs to be implemented')

    def get_url(self):
        return reverse('overview_list' + self.url_name_suffix)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # TODO: Maybe set theday to the start of the filter
        context.update({
            'current_date': date.today(),
            'theday': date.today(),
            'today_url': reverse('overview_today' + self.url_name_suffix),
            'day_hours': list(range(24)),
            'shifts': self.get_shifts(),
            'add_self_form': AddSelfParticipantForm(self.object, initial={'user': self.request.user}),
            'select_day_form': SelectDayForm(),
        })
        return context


class DetailListView(ListView):
    extra_context = {
        'day_calendar_template': 'cal/template/day_calendar_xs.html'
    }

    def get_shifts(self) -> Any:
        shift_filter = self.get_filters()
        shifts = Shift.objects.filter(shift_filter).order_by('start', 'end', 'shift_type')
        return [shift for shift in shifts if shift.can_see(self.request.user)]


class ShiftTypesListView(ListView):
    extra_context = {
        'day_calendar_template': 'cal/template/day_calendar_shift_types.html'
    }
    url_name_suffix = '_shift_types'

    def get_shifts(self):
        shift_filter = self.get_filters()
        shifts = Shift.objects.filter(shift_filter).order_by('start', 'shift_type')
        shifts = [shift for shift in shifts if shift.can_see_details(self.request.user)]
        add_default = False
        shift_idx_type = {
            'time_containers': {},
            'types': list(ShiftType.objects.filter(shift__in=shifts).distinct())
        }
        for shift in shifts:
            if shift.shift_type is None:
                add_default = True
                type_name = 'Default'
            else:
                type_name = shift.shift_type.name
            shift_idx_type['time_containers'].setdefault(shift.start.hour, {}).setdefault(type_name, []).append(shift)
        if add_default:
            shift_idx_type['types'].append(None)
        return shift_idx_type
