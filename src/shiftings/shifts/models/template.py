from datetime import datetime
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import Shift


class ShiftTemplate(models.Model):
    group = models.ForeignKey('ShiftTemplateGroup', on_delete=models.CASCADE, related_name='shifts',
                              verbose_name=_('Template Group'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))

    shift_type = models.ForeignKey('ShiftType', verbose_name=_('Shift Type'), on_delete=models.SET_NULL, blank=True,
                                   null=True)

    start_delay = models.DurationField(verbose_name=_('Start Delay'))
    duration = models.DurationField(verbose_name=_('Duration'))

    required_users = models.PositiveIntegerField(verbose_name=_('Required User'), default=0)
    max_users = models.PositiveIntegerField(verbose_name=_('Maximum User'), default=0)

    additional_infos = models.TextField(verbose_name=_('Additional Infos'), blank=True, null=True)

    class Meta:
        default_permissions = ()

    def create_shift(self, start: datetime, weekend_warning: Optional[str], holiday_warning: Optional[str]) -> Shift:
        warnings = None if weekend_warning is None else weekend_warning
        if holiday_warning:
            if warnings:
                warnings += f'\n{holiday_warning}'
            else:
                warnings = holiday_warning
        return Shift(name=self.name, shift_type=self.shift_type, place=self.group.place,
                     organization=self.group.organization, start=start, end=start + self.duration,
                     required_users=self.required_users, max_users=self.max_users,
                     additional_infos=self.additional_infos, warnings=warnings)
