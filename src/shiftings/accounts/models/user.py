from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

if TYPE_CHECKING:
    from shiftings.events.models import Event
    from shiftings.organizations.models import Organization


class BaseUser(AbstractUser):
    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.display

    @property
    def display(self) -> str:
        return self.get_full_name()


class User(BaseUser):
    display_name = models.CharField(max_length=150, verbose_name=_('Display Name'), null=True, blank=True)
    phone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['username']

    def __str__(self):
        return self.display

    @property
    def display(self) -> str:
        if self.display_name is None:
            return self.get_full_name()
        return self.display_name

    @property
    def organizations(self) -> QuerySet[Organization]:
        from shiftings.organizations.models import Organization
        return Organization.objects.filter(Q(members__user=self) |
                                           Q(members__group__in=self.groups.all())).distinct()

    @property
    def events(self) -> QuerySet[Event]:
        from shiftings.events.models import Event
        organizations = self.organizations
        return Event.objects.filter(
            Q(organization__in=organizations) | Q(allowed_organizations__in=organizations) | Q(public=True))

    @property
    def shift_count(self) -> int:
        from shiftings.shifts.models import Shift
        total = Shift.objects.filter(participants__user=self).count()
        for claimed_user in self.claimed_org_dummy_users.all():
            total += Shift.objects.filter(participants__user=claimed_user).count()
        return total
