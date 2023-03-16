from calendar import day_name, HTMLCalendar
from datetime import date
from typing import Any, Dict, List, Union

from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.cal.views.calendar_base import CalendarBaseView
from shiftings.shifts.models import RecurringShift, Shift


class MonthCalenderView(CalendarBaseView):
    template_name = 'cal/month_calendar.html'
    title = _('Calendar')

    def get_date(self) -> date:
        _date = date.today().replace(day=1)
        month = self.kwargs.get('themonth', None)
        year = self.kwargs.get('theyear', None)
        if month is not None:
            try:
                _date = _date.replace(month=int(month))
            except ValueError:
                pass
        if year is not None:
            try:
                _date = _date.replace(year=int(year))
            except ValueError:
                pass
        return _date

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data()
        _date = self.get_date()
        cal = MonthCalendar(_date, self.request.user, self.request, self.get_filters())
        html_calendar = cal.format()
        context_data['calendar'] = mark_safe(html_calendar)
        return context_data


class BaseCalendar(HTMLCalendar):
    _date: date
    user: User

    render_entries_as_form: bool = False

    def __init__(self, _date: date, user: User, request, shift_filter) -> None:
        super().__init__()
        self._date = _date
        self.user = user
        self.request = request
        self.shift_filter = shift_filter

    def get_shifts(self, _date: date) -> Union[List[Shift], QuerySet[Shift]]:

        time_filter = (Q(start__date=_date) | Q(end__date=_date, end__gt=_date) |
                       Q(start__lt=_date, end__gt=_date))
        return Shift.objects.filter(self.shift_filter & time_filter).order_by('start', 'end')

    def can_see_shift(self, shift: Shift) -> bool:
        return True  # shift.can_view(self.user)

    def get_shift_link(self, shift: Shift) -> str:
        return shift.get_absolute_url()

    def get_recurring_shifts(self, _date: date) -> List[RecurringShift]:
        if _date < date.today():
            return []
        r_shifts = RecurringShift.objects.all()
        if self.request.GET.get('filter') == 'own':
            return []
        if self.request.GET.get('filter') == 'organization' and 'organization' in self.request.GET:
            r_shifts = r_shifts.filter(organization__pk=self.request.GET.get('organization'))
        return [recurring_shift for recurring_shift in r_shifts if
                recurring_shift.matches_day(_date) and recurring_shift.enabled]

    def can_see_recurring_shift(self, recurring_shift: RecurringShift) -> bool:
        return False

    def get_recurring_shift_link(self, recurring_shift: RecurringShift, _date: date) -> str:
        params = {'date': _date}
        return f'{recurring_shift.get_absolute_url()}?{urlencode(params)}'

    def get_nav_url(self, args) -> str:  # pylint: disable=no-self-use
        return reverse('overview_month', args=args)

    def format(self) -> str:
        last_month = self._date - relativedelta(months=1)
        next_month = self._date + relativedelta(months=1)
        context = {
            'month': self._date,
            'weekday_names': day_name,
            'weeks': self.get_weeks(),
            'last_url': self.get_nav_url([last_month.month, last_month.year]),
            'next_url': self.get_nav_url([next_month.month, next_month.year])
        }
        return render_to_string('cal/template/month_calendar.html', context=context,
                                request=self.request)

    def render_shift(self, shift: Shift) -> str:
        context = {
            'shift': shift,
            'shift_link': self.get_shift_link(shift),
            'is_form': self.render_entries_as_form
        }
        return render_to_string('cal/calendar_templates/shift_entry.html', context, request=self.request)

    def render_recurring_shift(self, recurring_shift: RecurringShift, _date: date) -> str:
        context = {
            'recurring_shift': recurring_shift,
            'recurring_shift_link': self.get_recurring_shift_link(recurring_shift, _date),
        }
        return render_to_string('cal/calendar_templates/recurring_shift_entry.html', context, request=self.request)

    def get_day(self, day: int) -> Dict[str, Union[str, int, List[str]]]:
        if day == 0:
            # day outside month
            return {
                'class': 'noday',
                'name': '',
                'date': None,
                'entries': [],
            }

        _date = date(self._date.year, self._date.month, day)
        shifts = self.get_shifts(_date)
        recurring_shifts = self.get_recurring_shifts(_date)
        entries: List[str] = []
        if len(shifts) + len(recurring_shifts) > 0:
            shift: Shift
            for shift in shifts:
                if not self.can_see_shift(shift):
                    continue
                entries.append(self.render_shift(shift))
            for r_shift in recurring_shifts:
                if self.can_see_recurring_shift(r_shift) and not r_shift.shifts_exist(_date):
                    entries.append(self.render_recurring_shift(r_shift, _date))
        return {
            'class': 'day',
            'name': day,
            'date': _date,
            'entries': entries,
            'today': 'today' if date.today() == _date else '',
        }

    def get_weeks(self) -> List[List[Dict[str, Union[str, int, List[str]]]]]:
        weeks = []
        for week in self.monthdays2calendar(self._date.year, self._date.month):
            weeks.append([self.get_day(d) for d, _ in week])
        return weeks


class MonthCalendar(BaseCalendar):
    def can_see_recurring_shift(self, recurring_shift: RecurringShift) -> bool:
        return any(membership.is_member(self.user) for membership in recurring_shift.organization.members.all())

    def can_see_shift(self, shift: Shift) -> bool:
        return shift.can_see(self.user)
