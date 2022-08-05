from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class ShiftType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), unique=True)

    class Meta:
        default_permissions = ()
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class ShiftTypeGroup(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     related_name='shift_type_groups')
    position = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100, verbose_name=_('Group Name'))
    shift_types = models.ManyToManyField('ShiftType', verbose_name=_('Shift Types'))

    class Meta:
        default_permissions = ()
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'position'],
                                    name='shift_type_group_position_unique_constraint'),
            models.UniqueConstraint(fields=['organization', 'name'], name='shift_type_group_name_unique_constraint')
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display(self) -> str:
        return self.name
