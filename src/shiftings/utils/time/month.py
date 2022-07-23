from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import IntegerChoices
from django.db.models.fields import PositiveSmallIntegerField
from django.utils.translation import ugettext_lazy as _


class Month(IntegerChoices):
    January = 1, _('January')
    February = 2, _('February')
    March = 3, _('March')
    April = 4, _('April')
    May = 5, _('May')
    June = 6, _('June')
    July = 7, _('July')
    August = 8, _('August')
    September = 9, _('September')
    October = 10, _('October')
    November = 11, _('November')
    December = 12, _('December')


class MonthField(PositiveSmallIntegerField):
    def __init__(self, choices: Any = None, verbose_name: str = _('Month'), validators: Any = None,
                 **kwargs: Any) -> None:
        super().__init__(choices=(choices or Month.choices), verbose_name=verbose_name,
                         validators=(validators or [MinValueValidator(1), MaxValueValidator(12)]), **kwargs)


class MonthDayField(PositiveSmallIntegerField):
    def __init__(self, verbose_name: str = _('Day of the Month'), validators: Any = None,
                 **kwargs: Any) -> None:
        super().__init__(verbose_name=verbose_name,
                         validators=(validators or [MinValueValidator(1), MaxValueValidator(31)]), **kwargs)
