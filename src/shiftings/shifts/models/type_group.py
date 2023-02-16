from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from shiftings.organizations.models import Organization


class ShiftTypeGroup(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     verbose_name=_('Organization'), related_name='shift_type_groups')
    order = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100, verbose_name=_('Name'))

    class Meta:
        default_permissions = ()
        ordering = ['organization', 'order']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'order'],
                                    name='shift_type_group_organization_order_unique_constraint'),
            models.UniqueConstraint(fields=['organization', 'name'],
                                    name='shift_type_group_organization_name_unique_constraint'),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display(self) -> str:
        return self.name

    @staticmethod
    def get_next_free_order(organization: Organization) -> int:
        return ShiftTypeGroup.objects.filter(organization=organization).aggregate(models.Max('order'))['order__max'] + 1
