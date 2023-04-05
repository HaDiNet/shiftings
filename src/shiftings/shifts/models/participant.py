from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from shiftings.shifts.models import Shift


class Participant(models.Model):
    user = models.ForeignKey('accounts.BaseUser', on_delete=models.CASCADE, verbose_name=_('User'),
                             related_name='shifts')
    display_name = models.CharField(max_length=100, verbose_name=_('Display Name'), blank=True, null=True,
                                    help_text=_('Display Name is optional, and will be shown instead of the username'))
    confirmed = models.BooleanField(verbose_name=_('Participation confirmed'), default=False,
                                    help_text=_('Whether the participant has taken part in the shift or not. '
                                                'Default: False'))

    class Meta:
        default_permissions = ()
        ordering = ['display_name', 'user']

    def __str__(self):
        return f'{self.display} ({self.shift.display})'

    @property
    def display(self) -> str:
        return self.display_name or self.user.display

    @property
    def shift(self) -> Shift:
        return self.shift_set.first()

    def get_absolute_url(self) -> str:
        return self.shift.get_absolute_url()
