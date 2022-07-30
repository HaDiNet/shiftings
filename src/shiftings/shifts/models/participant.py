from django.db import models
from django.utils.translation import gettext_lazy as _


class Participant(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('User'), related_name='shifts')
    display_name = models.CharField(max_length=100, verbose_name=_('Display Name'), blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['display_name', 'user']

    def get_absolute_url(self) -> str:
        return self.shift.first().get_absolute_url()
