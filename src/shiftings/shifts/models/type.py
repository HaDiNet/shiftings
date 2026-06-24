from __future__ import annotations

from decimal import Decimal
from typing import Any, TYPE_CHECKING

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

from shiftings.utils.fields.html_color import calc_text_color

if TYPE_CHECKING:
    from shiftings.organizations.models import Organization


class ShiftTypeManager(models.Manager):
    def all(self, *, include_system: bool = False) -> QuerySet[ShiftType]:
        if include_system:
            return super().all()
        return super().all().filter(~Q(name='System'))

    def filter(self, *args: Any, include_system: bool = False, **kwargs: Any) -> QuerySet[ShiftType]:
        if include_system:
            return super().filter(*args, **kwargs)
        return super().filter(*args, ~Q(name='System'), **kwargs)

    def organization(self, organization: Organization, include_system: bool = False) -> QuerySet[ShiftType]:
        return self.filter(organization=organization, include_system=include_system)

    def system(self, organization: Organization) -> ShiftType | None:
        return super().filter(organization=organization, name='System').first()


class ShiftType(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     verbose_name=_('Organization'), related_name='shift_types')
    group = models.ForeignKey('ShiftTypeGroup', on_delete=models.SET_NULL, verbose_name=_('Group'),
                              related_name='shift_types', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    color = ColorField(default='#FD7E14', format='hex', samples=settings.SHIFT_COLOR_PALETTE)

    is_mandatory = models.BooleanField(verbose_name=_('Mandatory Shift Type'), default=False,
                                       help_text=_('When set, members who do not respond to shifts of this type '
                                                   'incur the organisation-wide no-response penalty. Only takes '
                                                   'effect when the organisation has Session Points enabled.'))
    point_weight = models.DecimalField(verbose_name=_('Session Points Weight'), max_digits=4, decimal_places=2,
                                       default=Decimal('1.00'),
                                       help_text=_('Points awarded when attending a shift of this type. Only takes '
                                                   'effect when the organisation has Session Points enabled.'))

    objects = ShiftTypeManager()

    class Meta:
        default_permissions = ()
        ordering = ['group', 'name']
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
    def choice(self) -> tuple[int, str]:
        return self.pk, self.name

    @property
    def text_color(self):
        return calc_text_color(self.color)

    @property
    def is_system(self) -> bool:
        return self.name == 'System'
