from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import holidays
from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import DurationField
from django.urls import reverse
from django.utils.translation import gettext as __, gettext_lazy as _

from shiftings.shifts.utils.time_frame import TimeFrameType
from shiftings.utils.fields.date_time import DateField, TimeField
from shiftings.utils.time.month import Month, MonthField
from shiftings.utils.time.week import WeekDay, WeekDayField
from .shift import Shift
from .shift_base import ShiftBase


class ProblemHandling(models.IntegerChoices):
    Ignore = 1, _('ignore')
    Cancel = 2, _('cancel')
    Warn = 3, _('show warning')


class RecurringShift(ShiftBase):
    time_frame_field = models.PositiveSmallIntegerField(choices=TimeFrameType.choices, verbose_name=_('Timeframe Type'))
    ordinal = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(31)])
    week_day_field = WeekDayField(blank=True, null=True)
    month_field = MonthField(blank=True, null=True)
    first_occurrence = DateField(_('First Occurrence'))
    time = TimeField(verbose_name=_('Time'))
    duration = DurationField(verbose_name=_('Duration'))

    weekend_handling_field = models.PositiveSmallIntegerField(choices=ProblemHandling.choices,
                                                              verbose_name=_('Weekend problem handling'),
                                                              default=ProblemHandling.Ignore)
    weekend_warning = models.TextField(verbose_name=_('Warning text for weekend'), blank=True, null=True)

    holiday_handling_field = models.PositiveSmallIntegerField(choices=ProblemHandling.choices,
                                                              verbose_name=_('Holidays problem handling'),
                                                              default=ProblemHandling.Ignore)
    holiday_warning = models.TextField(verbose_name=_('Warning text for holidays'), blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['name', 'organization']

    def __str__(self) -> str:
        return self.display

    @property
    def display(self) -> str:
        return f'{self.name} ({self.repetition_display})'

    @property
    def time_frame_type(self) -> TimeFrameType:
        return TimeFrameType(self.time_frame_field)

    # noinspection PyUnresolvedReferences
    @property
    def repetition_display(self) -> str:
        return self.get_time_frame_field_display() \
            .replace(__('Nth'), str(ordinal(self.ordinal))) \
            .replace(__('[weekday]'), str(self.get_week_day_field_display())) \
            .replace(__('[month]'), str(self.get_month_field_display()))

    @property
    def week_day(self) -> Optional[WeekDay]:
        if self.week_day_field is not None:
            # noinspection PyTypeChecker
            return WeekDay(self.week_day_field)
        return None

    @property
    def month(self) -> Optional[Month]:
        if self.month_field is not None:
            # noinspection PyTypeChecker
            return Month(self.month_field)
        return None

    @property
    def weekend_handling(self) -> ProblemHandling:
        return ProblemHandling(self.weekend_handling_field)

    @property
    def holiday_handling(self) -> ProblemHandling:
        return ProblemHandling(self.holiday_handling_field)

    def clean(self) -> None:
        if self.week_day_field is None and self.time_frame_type in TimeFrameType.get_weekday_types():
            raise ValidationError(_('Weekday can\'t be empty with the chosen time frame type.'))
        if self.month_field is None and self.time_frame_field in TimeFrameType.get_monthday_types():
            raise ValidationError(_('Month can\'t be empty with the chosen time frame type.'))
        if self.weekend_handling is not ProblemHandling.Ignore and self.weekend_warning is None:
            raise ValidationError(_('You need to add a warning for weekend handling.'))
        if self.holiday_handling is not ProblemHandling.Ignore and self.holiday_warning is None:
            raise ValidationError(_('You need to add a warning for holiday handling.'))
        if not self.matches_day(self.first_occurrence):
            raise ValidationError(_('Your first occurrence doesn\'t match your chosen time frame.'))

    def shift_exists(self, _date: date) -> bool:
        return self.created_shifts.filter(start=datetime.combine(_date, self.time)).exists()

    def matches_day(self, _date: date) -> bool:
        return self.time_frame_type.matches_day(self, _date)

    def create_shift(self, _date: date) -> Optional[Shift]:
        if self.shift_exists(_date):
            return None

        start = datetime.combine(_date, self.time)
        shift = Shift(name=self.name, shift_type=self.shift_type, place=self.place, organization=self.organization,
                      start=start, end=start + self.duration, required_users=self.required_users,
                      max_users=self.max_users, additional_infos=self.additional_infos, based_on=self)
        if WeekDay.is_weekend(_date):
            if self.weekend_handling is ProblemHandling.Cancel:
                return None
            elif self.weekend_handling is ProblemHandling.Warn and self.weekend_warning is not None:
                shift.warnings = self.weekend_warning
        if _date in holidays.Germany(prov='BW'):
            if self.holiday_handling is ProblemHandling.Cancel:
                return None
            elif self.holiday_handling is ProblemHandling.Warn and self.holiday_warning is not None:
                if shift.warnings:
                    shift.warnings += f'\n{self.holiday_warning}'
                else:
                    shift.warnings = self.holiday_warning
        shift.save()
        return shift

    def get_absolute_url(self) -> str:
        return reverse('recurring_shift', args=[self.pk])
