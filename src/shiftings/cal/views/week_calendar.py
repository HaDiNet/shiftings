from calendar import HTMLCalendar, month_name, monthrange
from datetime import date, timedelta
from typing import Any, Optional, Union

from dateutil.relativedelta import relativedelta
from django.db.models import Q

from shiftings.cal.views.calendar_base import CalendarBaseView
from shiftings.events.models import Event
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Shift


class WeekView(CalendarBaseView):
    template_name = 'cal/day_calendar.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        theday = date.fromisoformat(self.kwargs.get('theday')) if 'theday' in self.kwargs else date.today()
        shift_filter = (Q(start__date=theday) | Q(end__date=theday) |
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
            # 'weeks': self.get_weeks(),
            # 'last_url': self.get_nav_url() + '?' + urlencode({
            #     'month': last_month.month,
            #     'year': last_month.year
            # }),
            # 'next_url': self.get_nav_url() + '?' + urlencode({
            #     'month': next_month.month,
            #     'year': next_month.year
            # })
        })
        return context

    def get_shift_day_metadata(self, day: date, shift: Shift):
        duration = 24
        if day == shift.end.date():
            end_hour = 24 - shift.end.hour
            duration = shift.end.hour
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


class WeekOverviewCalendar(HTMLCalendar):
    cssclass_week = "table table-dark m-0 text-center month-summary"
    active_days: Optional[set[int]] = None
    current_day: Optional[date]

    def __init__(self, model: Union[Event, Organization]):
        super().__init__()
        self.model = model

    def format(self, current_day: Optional[date] = None):
        if current_day is None:
            current_day = date.today
        self.current_day = current_day.replace(day=1)
        the_month, the_year = self.current_day.month, self.current_day.year
        if self.active_days is None:
            self.active_days = set()

        filter_start = date(the_year, the_month, 1)
        filter_end = date(the_year, the_month, monthrange(the_year, the_month)[1])
        for start in self.model.shifts.filter(start__range=[filter_start, filter_end]).values_list('start', flat=True):
            if start.month != the_month or start.year != the_year:
                continue
            self.active_days.add(start.day)
        return self.formatmonth(the_year, the_month)

    def formatmonthname(self, theyear: int, themonth: int, withyear: bool = True) -> str:
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        prev_month = self.current_day.replace(day=1) - relativedelta(months=1)
        next_month = self.current_day.replace(day=1) + relativedelta(months=1)
        return (f'<tr>'
                f'<th class="pe-pointer"'
                f' onclick="window.location.href=\'?month={prev_month.month}&year={prev_month.year}\'">'
                f'<i class="fas fa-left-long"></i></th>'
                f'<th colspan="5" class="{self.cssclass_month_head}">{s}</th>'
                f'<th class="pe-pointer"'
                f' onclick="window.location.href=\'?month={next_month.month}&year={next_month.year}\'">'
                f'<i class="fas fa-right-long"></i></th>'
                f'</tr>')

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            # day outside month
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        else:
            if day in self.active_days:
                day_url = ''
                return f'<td class="{self.cssclasses[weekday]}"><a class="link" href="{day_url}">{day}</a></td>'
            else:
                return f'<td class="{self.cssclasses[weekday]} disabled">{day}</td>'
