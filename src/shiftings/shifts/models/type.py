from __future__ import annotations

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from shiftings.utils.fields.html_color import calc_text_color


class ShiftType(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     verbose_name=_('Organization'), related_name='shift_types')
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    color = ColorField(default='#FD7E14', format='hex', samples=settings.SHIFT_COLOR_PALETTE)

    class Meta:
        default_permissions = ()
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'name'],
                                    name='shift_type_organization_name_unique_constraint'),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display(self) -> str:
        return self.name

    @property
    def text_color(self):
        return calc_text_color(self.color)
