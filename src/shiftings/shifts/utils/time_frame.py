from __future__ import annotations

from datetime import date, timedelta
from math import ceil
from typing import List, TYPE_CHECKING

from django.db import models
from django.utils.translation import ugettext_lazy as _

from shiftings.utils.time.week import WeekDay

if TYPE_CHECKING:
    from shiftings.shifts.models import RecurringShift


class TimeFrameType(models.IntegerChoices):
    NthWeekdayOfTheMonth = 1, _('Nth [weekday] of each month')
    NthDayOfTheMonth = 2, _('Nth day of each month')
    EveryNthWeekday = 3, _('every Nth [weekday]')
    NthWorkdayOfTheMonth = 4, _('Nth workday of each month')
    NthDayOfASpecificMonth = 5, _('Nth day of [month]')
    NthWorkdayOfASpecificMonth = 6, _('Nth workday of [month]')

    def matches_day(self, shift: RecurringShift, _date: date) -> bool:
        if self is TimeFrameType.NthWeekdayOfTheMonth:
            return self._matches_nth_weekday_of_the_month(shift, _date)
        if self is TimeFrameType.NthDayOfTheMonth:
            return self._matches_nth_day_of_the_month(shift, _date)
        if self is TimeFrameType.EveryNthWeekday:
            return self._matches_every_nth_weekday(shift, _date)
        if self is TimeFrameType.NthWorkdayOfTheMonth:
            return self._matches_nth_workday_of_the_month(shift, _date)
        if self is TimeFrameType.NthDayOfASpecificMonth:
            return self._matches_nth_day_of_a_specific_month(shift, _date)
        if self is TimeFrameType.NthWorkdayOfASpecificMonth:
            return self._matches_nth_workday_of_a_specific_month(shift, _date)
        return False

    @staticmethod
    def get_weekday_types() -> List[TimeFrameType]:
        return [TimeFrameType.NthWeekdayOfTheMonth, TimeFrameType.EveryNthWeekday]

    @staticmethod
    def get_monthday_types() -> List[TimeFrameType]:
        return [TimeFrameType.NthDayOfASpecificMonth, TimeFrameType.NthWorkdayOfASpecificMonth]

    @staticmethod
    def _matches_nth_weekday_of_the_month(shift: RecurringShift, _date: date) -> bool:
        if _date.weekday() != shift.week_day_field:
            return False
        occurrence = ceil(_date.day / 7)
        if occurrence == shift.ordinal:
            return True
        if occurrence > shift.ordinal:
            return False
        return (_date + timedelta(days=7)).month != _date.month

    @staticmethod
    def _matches_nth_day_of_the_month(shift: RecurringShift, _date: date) -> bool:
        if _date.day == shift.ordinal:
            return True
        return shift.ordinal > _date.day and (_date + timedelta(days=1)).month != _date.month

    @staticmethod
    def _matches_every_nth_weekday(shift: RecurringShift, _date: date) -> bool:
        if _date.weekday() != shift.week_day_field:
            return False
        if shift.ordinal == 1:
            return True
        if _date == shift.first_occurrence:
            return True
        weeks = (_date - shift.first_occurrence).days / 7
        return weeks % shift.ordinal == 0

    @staticmethod
    def _matches_nth_workday_of_the_month(shift: RecurringShift, _date: date) -> bool:
        if WeekDay.is_weekend(_date):
            return False
        workday = 0
        for i in range(1, _date.day + 1):
            if not WeekDay.is_weekend(date(_date.year, _date.month, i)):
                workday = workday + 1
        if workday == shift.ordinal:
            return True
        return shift.ordinal > workday and TimeFrameType._next_workday(_date).month != _date.month

    @staticmethod
    def _next_workday(_date: date) -> date:
        _next = _date + timedelta(days=1)
        while WeekDay.is_weekend(_next):
            _next += timedelta(days=1)
        return _next

    @staticmethod
    def _matches_nth_day_of_a_specific_month(shift: RecurringShift, _date: date) -> bool:
        return _date.month == shift.month_field and TimeFrameType._matches_nth_day_of_the_month(shift, _date)

    @staticmethod
    def _matches_nth_workday_of_a_specific_month(shift: RecurringShift, _date: date) -> bool:
        return _date.month == shift.month_field \
               and TimeFrameType._matches_nth_workday_of_the_month(shift, _date)
