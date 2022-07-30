from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .shift_base import ShiftBase
from ...utils.fields.date_time import DateTimeField

if TYPE_CHECKING:
    from ...accounts.models import User


class Shift(ShiftBase):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='shifts', verbose_name=_('Event'),
                              blank=True, null=True)

    start = DateTimeField(verbose_name=_('Start Date and Time'), db_index=True)
    end = DateTimeField(verbose_name=_('End Date and Time'), db_index=True)

    participants = models.ManyToManyField('shifts.Participant', verbose_name=_('Users'), blank=True,
                                          related_name='shift')

    locked = models.BooleanField(verbose_name=_('Locked for Participation'), default=False)
    warnings = models.TextField(verbose_name=_('Warning'), blank=True, null=True)

    based_on = models.ForeignKey('RecurringShift', on_delete=models.SET_NULL, related_name='created_shifts',
                                 verbose_name=_('Created by Recurring Shift'), blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['start', 'end', 'name', 'organization']

    def __str__(self) -> str:
        return _('Shift {name} on {time}').format(name=self.name, time=self.start.strftime("%Y-%m-%d %H:%M:%S"), )

    @property
    def display(self) -> str:
        return self.name

    @property
    def is_full(self):
        return self.max_users != 0 and len(self.participants.all()) >= self.max_users

    def get_slots_display(self) -> Optional[list[tuple[Union[bool, User], bool]]]:
        slots = []
        if self.required_users != 0:
            slots = [(False, True) for i in range(self.required_users)]
        if self.max_users != 0:
            slots += [(False, False) for i in range(self.max_users - self.required_users)]
        for i, user in enumerate(self.participants.all()):
            try:
                slots[i] = user, slots[i][1]
            except IndexError:
                slots.append((user, False))
        return slots

    def get_absolute_url(self) -> str:
        return reverse('shift', args=[self.pk])
