from django.db import models
from django.utils.translation import gettext_lazy as _


class ShiftBase(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    shift_type = models.ForeignKey('ShiftType', verbose_name=_('Shift Type'), on_delete=models.SET_NULL, blank=True,
                                   null=True)
    place = models.CharField(max_length=255, verbose_name=_('Place'))

    required_shifters = models.PositiveIntegerField(verbose_name=_('Required Shifters'), default=0)
    max_shifters = models.PositiveIntegerField(verbose_name=_('Maximum Shifters'), default=0)

    # TODO: required permissions
    additional_infos = models.TextField(verbose_name=_('Additional Infos'), blank=True, null=True)

    class Meta:
        abstract = True
        default_permissions = ()
