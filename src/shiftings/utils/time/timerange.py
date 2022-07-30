import calendar
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeRangeType(models.IntegerChoices):
    Month = 1, _('Month')
    Quarter = 2, _('Quarter')
    HalfYear = 3, _('Half Year')
    Year = 4, _('Year')
    Decade = 5, _('Decade')
    Century = 6, _('Century')
    Millennium = 7, _('Millennium')

    def get_time_range(self, year: int, month: int) -> tuple[datetime, datetime]:
        start_year, end_year = self.get_years(year)
        start_month, end_month = self.get_months(month)
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
