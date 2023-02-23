from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.utils.fields.date_time import DateTimeField
from .base import ShiftBase

if TYPE_CHECKING:
    from shiftings.accounts.models import User


class Shift(ShiftBase):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='shifts', verbose_name=_('Event'),
                              blank=True, null=True)

    start = DateTimeField(verbose_name=_('Start Date and Time'), db_index=True)
    end = DateTimeField(verbose_name=_('End Date and Time'), db_index=True)

    participants = models.ManyToManyField('shifts.Participant', verbose_name=_('Users'), blank=True,
                                          related_name='shift_set')

    locked = models.BooleanField(verbose_name=_('Locked for Participation'), default=False)
    warnings = models.TextField(max_length=500, verbose_name=_('Warning'), blank=True, null=True,
                                help_text=_('A maximum of {amount} characters is allowed').format(amount=500))

    based_on = models.ForeignKey('RecurringShift', on_delete=models.SET_NULL, related_name='created_shifts',
                                 verbose_name=_('Created by Recurring Shift'), blank=True, null=True)

    created = DateTimeField(verbose_name=_('Created'), auto_now_add=True)
    modified = DateTimeField(verbose_name=_('Last Modified'), auto_now=True)

    class Meta:
        default_permissions = ()
        ordering = ['start', 'end', 'name', 'organization']
        constraints = [
            models.CheckConstraint(check=Q(start__lte=F('end')), name='shift_start_before_end')
        ]

    def clean(self) -> None:
        if self.event and self.event.organization != self.organization:
            raise ValidationError(_('Organization and Event Organization must be identical.'))

    def __str__(self) -> str:
        return _('Shift {name} on {time}').format(name=self.name, time=self.start.strftime("%Y-%m-%d %H:%M:%S"), )

    @property
    def display(self) -> str:
        return self.name

    @property
    def detailed_display(self) -> str:
        return _('{name} from {start} to {end} ').format(name=self.name,
                                                         start=self.start.strftime("%Y-%m-%d %H:%M"),
                                                         end=self.end.strftime("%Y-%m-%d %H:%M"))

    @property
    def time_display(self) -> str:
        if self.start.date() != self.end.date():
            return _('{start} to {end_time} on {end_date} ').format(name=self.name,
                                                                    start=self.start.strftime("%H:%M"),
                                                                    end_time=self.end.strftime("%H:%M"),
                                                                    end_date=self.end.date())
        return _('{start} to {end_time}').format(name=self.name,
                                                 start=self.start.strftime("%H:%M"),
                                                 end_time=self.end.strftime("%H:%M"), )

    @property
    def is_full(self):
        return self.max_users != 0 and len(self.participants.all()) >= self.max_users

    @property
    def email(self) -> str:
        if self.event and self.event.email:
            return self.event.email
        return self.organization.email

    def get_slots_display(self) -> Optional[list[tuple[Union[bool, User], bool]]]:
        slots = []
        if self.required_users != 0:
            slots = [(False, True) for i in range(self.required_users)]
        if self.max_users != 0:
            slots += [(False, False) for i in range(self.max_users - self.required_users)]
        for i, user in enumerate(self.participants.all().order_by('pk')):
            try:
                slots[i] = user, slots[i][1]
            except IndexError:
                slots.append((user, False))
        return slots

    def can_see(self, user: User) -> bool:
        if self.participants.filter(user=user).exists():
            return True
        if self.event:
            return self.event.can_see(user)
        return self.organization.is_member(user)

    def is_participant(self, user: User) -> bool:
        return user.pk in self.participants.values_list('user__pk', flat=True)

    def get_absolute_url(self) -> str:
        return reverse('shift', args=[self.pk])
