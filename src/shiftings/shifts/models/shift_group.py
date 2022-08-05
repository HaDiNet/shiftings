from __future__ import annotations

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class ShiftGroup(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     verbose_name=_('Organization'), related_name='shift_groups', blank=True, null=True)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, verbose_name=_('Event'),
                              related_name='shift_groups', blank=True, null=True)

    name = models.CharField(max_length=100, verbose_name=_('Name'), unique=True)
    position = models.PositiveSmallIntegerField()
    color = ColorField(default='#FD7E14', format='hex', samples=settings.SHIFT_COLOR_PALETTE)

    class Meta:
        default_permissions = ()
        ordering = ['position', 'name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'position'],
                                    name='shift_group_organization_position_unique_constraint'),
            models.UniqueConstraint(fields=['event', 'position'], name='shift_group_event_position_unique_constraint'),
            models.UniqueConstraint(fields=['organization', 'name'],
                                    name='shift_group_organization_name_unique_constraint'),
            models.UniqueConstraint(fields=['event', 'name'], name='shift_group_event_name_unique_constraint'),
            models.CheckConstraint(
                check=Q(organization__isnull=True, event__isnull=False) | Q(organization__isnull=False,
                                                                            event__isnull=True),
                name='shift_group_name_or_organization')
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display(self) -> str:
        return self.name
