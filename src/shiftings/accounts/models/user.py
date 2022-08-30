from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from shiftings.events.models import Event
from shiftings.organizations.models import Organization


class User(AbstractUser):
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
        return Organization.objects.filter(Q(all_members__user=self) |
                                           Q(all_members__group__in=self.groups.all())).distinct()

    @property
    def events(self) -> QuerySet[Event]:
        return Event.objects.filter(Q(organization__all_members__user=self) | Q(public=True) |
                                    Q(organization__all_members__group__in=self.groups.all())).distinct()
