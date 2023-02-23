from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from shiftings.shifts.models import Shift


class ShiftTemplate(models.Model):
    group = models.ForeignKey('ShiftTemplateGroup', on_delete=models.CASCADE, related_name='shifts',
                              verbose_name=_('Template Group'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))

    shift_type = models.ForeignKey('ShiftType', verbose_name=_('Shift Type'), on_delete=models.SET_NULL, blank=True,
                                   null=True)

    start_delay = models.DurationField(verbose_name=_('Start Delay'))
    duration = models.DurationField(verbose_name=_('Duration'))

    required_users = models.PositiveSmallIntegerField(verbose_name=_('Required User'), default=0,
                                                      validators=[MaxValueValidator(32)],
                                                      help_text=_('A maximum of 32 users can be required'))
    max_users = models.PositiveSmallIntegerField(verbose_name=_('Maximum User'), default=0,
                                                 validators=[MaxValueValidator(64)],
                                                 help_text=_('A maximum of 64 users can be present'))

    additional_infos = models.TextField(max_length=1000, verbose_name=_('Additional Infos'), blank=True, null=True,
                                        help_text=_('A maximum of {amount} characters is allowed').format(amount=1000))

    class Meta:
        default_permissions = ()

    def create_shift(self, start: datetime, weekend_warning: Optional[str], holiday_warning: Optional[str]) -> Shift:
        warnings = None if weekend_warning is None else weekend_warning
        if holiday_warning:
            if warnings:
                warnings += f'\n{holiday_warning}'
            else:
                warnings = holiday_warning
        from shiftings.shifts.models import Shift
        return Shift(name=self.name, shift_type=self.shift_type, place=self.group.place,
                     organization=self.group.organization, start=start, end=start + self.duration,
                     required_users=self.required_users, max_users=self.max_users,
                     additional_infos=self.additional_infos, warnings=warnings)
