from __future__ import annotations

from datetime import date
from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import IntegerChoices
from django.db.models.fields import PositiveSmallIntegerField
from django.utils.translation import gettext_lazy as _


class WeekDay(IntegerChoices):
    Monday = 0, _('Monday')
    Tuesday = 1, _('Tuesday')
    Wednesday = 2, _('Wednesday')
    Thursday = 3, _('Thursday')
    Friday = 4, _('Friday')
    Saturday = 5, _('Saturday')
    Sunday = 6, _('Sunday')

    @staticmethod
    def is_weekend(_date: date) -> bool:
        return _date.weekday() in [WeekDay.Saturday.value, WeekDay.Sunday.value]


class WeekDayField(PositiveSmallIntegerField):
    def __init__(self, choices: Any = None, verbose_name: str = _('Day of the Week'), validators: Any = None,
                 **kwargs: Any) -> None:
        super().__init__(choices=(choices or WeekDay.choices), verbose_name=verbose_name,
                         validators=(validators or [MinValueValidator(0), MaxValueValidator(6)]), **kwargs)
