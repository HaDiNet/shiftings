from django.db import models
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import Shift


class Participant(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('User'), related_name='shifts')
    display_name = models.CharField(max_length=100, verbose_name=_('Display Name'), blank=True, null=True,
                                    help_text=_('Display Name is optional'))

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
