from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Membership(models.Model):
    shifter = models.ForeignKey('Shifter', on_delete=models.CASCADE, related_name='memberships',
                                verbose_name=_('Shifter'), blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships', verbose_name=_('Group'),
                              blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['group', 'shifter']

    def __str__(self) -> str:
        return self.shifter.name if self.shifter else self.group.name

    @property
    def is_shifter(self) -> bool:
        return self.shifter is not None

    def clean(self) -> None:
        if self.shifter and self.group:
            raise ValidationError(_('Membership can only be either shifter or group, not both.'))
        if not self.shifter and not self.group:
            raise ValidationError(_('Membership must consist of a shifter or a group.'))
