from datetime import date, datetime

from django.test import TestCase

from shiftings.utils.time.timerange import TimeRangeType


class TimeRangeTest(TestCase):
    def test_correct_time(self) -> None:
        start, end = TimeRangeType.Month.get_time_range(2022, 5)
        self.assertEqual(start, datetime(2022, 5, 1))
        self.assertEqual(end, datetime(2022, 5, 31, 23, 59, 59, 999999))

    def test_month(self) -> None:
        start, end = TimeRangeType.Month.get_time_range(2022, 5)
        self.assertEqual(start, datetime(2022, 5, 1))
        self.assertEqual(end.date(), date(2022, 5, 31))
        start, end = TimeRangeType.Month.get_time_range(2022, 2)
        self.assertEqual(start, datetime(2022, 2, 1))
        self.assertEqual(end.date(), date(2022, 2, 28))
        start, end = TimeRangeType.Month.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2024, 2, 1))
        self.assertEqual(end.date(), date(2024, 2, 29))
        start, end = TimeRangeType.Month.get_time_range(2022, 6)
        self.assertEqual(start, datetime(2022, 6, 1))
        self.assertEqual(end.date(), date(2022, 6, 30))

    def test_quarter(self) -> None:
        start, end = TimeRangeType.Quarter.get_time_range(2022, 6)
        self.assertEqual(start, datetime(2022, 4, 1))
        self.assertEqual(end.date(), date(2022, 6, 30))
        start, end = TimeRangeType.Quarter.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2024, 1, 1))
        self.assertEqual(end.date(), date(2024, 3, 31))
        start, end = TimeRangeType.Quarter.get_time_range(2022, 1)
        self.assertEqual(start, datetime(2022, 1, 1))
        self.assertEqual(end.date(), date(2022, 3, 31))

    def test_half_year(self) -> None:
        start, end = TimeRangeType.HalfYear.get_time_range(2022, 6)
        self.assertEqual(start, datetime(2022, 1, 1))
        self.assertEqual(end.date(), date(2022, 6, 30))
        start, end = TimeRangeType.HalfYear.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2024, 1, 1))
        self.assertEqual(end.date(), date(2024, 6, 30))
        start, end = TimeRangeType.HalfYear.get_time_range(2022, 9)
        self.assertEqual(start, datetime(2022, 7, 1))
        self.assertEqual(end.date(), date(2022, 12, 31))
        start, end = TimeRangeType.HalfYear.get_time_range(2022, 12)
        self.assertEqual(start, datetime(2022, 7, 1))
        self.assertEqual(end.date(), date(2022, 12, 31))

    def test_year(self) -> None:
        start, end = TimeRangeType.Year.get_time_range(2022, 6)
        self.assertEqual(start, datetime(2022, 1, 1))
        self.assertEqual(end.date(), date(2022, 12, 31))
        start, end = TimeRangeType.Year.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2024, 1, 1))
        self.assertEqual(end.date(), date(2024, 12, 31))
        start, end = TimeRangeType.Year.get_time_range(2022, 9)
        self.assertEqual(start, datetime(2022, 1, 1))
        self.assertEqual(end.date(), date(2022, 12, 31))

    def test_decade(self) -> None:
        start, end = TimeRangeType.Decade.get_time_range(2022, 6)
        self.assertEqual(start, datetime(2020, 1, 1))
        self.assertEqual(end.date(), date(2029, 12, 31))
        start, end = TimeRangeType.Decade.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2020, 1, 1))
        self.assertEqual(end.date(), date(2029, 12, 31))
        start, end = TimeRangeType.Decade.get_time_range(2022, 9)
        self.assertEqual(start, datetime(2020, 1, 1))
        self.assertEqual(end.date(), date(2029, 12, 31))

    def test_century(self) -> None:
        start, end = TimeRangeType.Century.get_time_range(1999, 6)
        self.assertEqual(start, datetime(1900, 1, 1))
        self.assertEqual(end.date(), date(1999, 12, 31))
        start, end = TimeRangeType.Century.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2000, 1, 1))
        self.assertEqual(end.date(), date(2099, 12, 31))
        start, end = TimeRangeType.Century.get_time_range(2122, 9)
        self.assertEqual(start, datetime(2100, 1, 1))
        self.assertEqual(end.date(), date(2199, 12, 31))

    def test_millennium(self) -> None:
        start, end = TimeRangeType.Millennium.get_time_range(1999, 12)
        self.assertEqual(start, datetime(1000, 1, 1))
        self.assertEqual(end.date(), date(1999, 12, 31))
        start, end = TimeRangeType.Millennium.get_time_range(2024, 2)
        self.assertEqual(start, datetime(2000, 1, 1))
        self.assertEqual(end.date(), date(2999, 12, 31))
        start, end = TimeRangeType.Millennium.get_time_range(2122, 9)
        self.assertEqual(start, datetime(2000, 1, 1))
        self.assertEqual(end.date(), date(2999, 12, 31))
