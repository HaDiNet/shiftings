from __future__ import annotations

from django.db import models
from django.db.models import DateTimeField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import Shifter
from .shift_base import ShiftBase


class Shift(ShiftBase):
    start = DateTimeField(verbose_name=_('Start Date and Time'), db_index=True)
    end = DateTimeField(verbose_name=_('End Date and Time'), db_index=True)

    shifters = models.ManyToManyField('accounts.Shifter', related_name='shifts', verbose_name=_('Shifters'), blank=True)

    locked = models.BooleanField(verbose_name=_('Locked for Participation'), default=False)
    warnings = models.TextField(verbose_name=_('Warning'), blank=True, null=True)

    based_on = models.ForeignKey('RecurringShift', on_delete=models.SET_NULL, related_name='created_shifts',
                                 verbose_name=_('Created by Recurring Shift'), blank=True, null=True)
    created_by = models.ForeignKey('accounts.Shifter', on_delete=models.SET_NULL, related_name='created_shifts',
                                   verbose_name=_('Created by Shifter'), blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['start', 'end', 'name']

    def __str__(self) -> str:
        return _('Shift {name} on {time}').format(name=self.name, time=self.start.strftime("%Y-%m-%d %H:%M:%S"), )

    @property
    def display(self) -> str:
        return self.name

    def was_created_by(self, user: Shifter) -> bool:
        return self.created_by is not None and self.created_by.pk == user.pk

    def get_absolute_url(self) -> str:
        return reverse('shift', args=[self.pk])
