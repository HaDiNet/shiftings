import calendar
from datetime import date, datetime, MINYEAR, MAXYEAR
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from shiftings.utils.time.month import Month


class TimeRangeType(models.IntegerChoices):
    Month = 1, _('Month')
    Quarter = 2, _('Quarter')
    HalfYear = 3, _('Half Year')
    Year = 4, _('Year')
    Decade = 5, _('Decade')
    Century = 6, _('Century')
    Millennium = 7, _('Millennium')

    def display(self, year: Optional[int] = None, month: Optional[int] = None) -> str:
        if year is None:
            year = date.today().year
        else:
            year = min(max(year, MINYEAR), MAXYEAR)
        if month is None:
            month = date.today().month
        else:
            month = min(max(month, 1), 12)
        if self is TimeRangeType.Month:
            return f'{Month(month).label} {year}'
        if self is TimeRangeType.Quarter:
            return f'{(month - 1) // 3 + 1}. {self.label} {year}'
        if self is TimeRangeType.HalfYear:
            return f'{(month - 1) // 6 + 1}. {self.label} {year}'
        if self is TimeRangeType.Year:
            return f'{year}'
        start, end = self.get_time_range(year, month)
        return f'{start.year} - {end.year}'

    def get_time_range(self, year: int, month: int) -> tuple[datetime, datetime]:
        def fix_years(start: int, end: int) -> tuple[int, int]:
            return min(max(start, MINYEAR), MAXYEAR), min(max(end, MINYEAR), MAXYEAR)

        def fix_months(start: int, end: int) -> tuple[int, int]:
            return min(max(start, 1), 12), min(max(end, 1), 12)

        start_year, end_year = fix_years(*self.get_years(year))
        start_month, end_month = fix_months(*self.get_months(month))
        return (datetime(start_year, start_month, 1),
                datetime(end_year, end_month, calendar.monthrange(end_year, end_month)[1], 23, 59, 59, 999999))

    def get_months(self, month: int) -> tuple[int, int]:
        if self is TimeRangeType.Month:
            return month, month
        if self is TimeRangeType.Quarter:
            return self.calc_start_end(month, 3, 1)
        if self is TimeRangeType.HalfYear:
            return self.calc_start_end(month, 6, 1)
        return 1, 12

    def get_years(self, year: int) -> tuple[int, int]:
        if self is TimeRangeType.Decade:
            return self.calc_start_end(year, 10)
        if self is TimeRangeType.Century:
            return self.calc_start_end(year, 100)
        if self is TimeRangeType.Millennium:
            return self.calc_start_end(year, 1000)
        return year, year

    @staticmethod
    def calc_start_end(num: int, div: int, offset: int = 0) -> tuple[int, int]:
        return (start := (num - offset) // div * div + offset), start + div - 1
