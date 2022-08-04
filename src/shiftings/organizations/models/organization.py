from __future__ import annotations

from datetime import date
from typing import Optional, TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

from shiftings.organizations.models.membership import MembershipType

if TYPE_CHECKING:
    from shiftings.accounts.models import User
    from shiftings.events.models import Event
    from shiftings.shifts.models import Shift


class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), unique=True)
    logo = models.ImageField(verbose_name=_('Logo'), upload_to='upload/organizations/', blank=True, null=True)

    email = models.EmailField(verbose_name=_('E-Mail'), blank=True, null=True)
    telephone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)
    website = models.URLField(verbose_name=_('Website'), blank=True, null=True,
                              help_text=_('Include Protocol i.E. https://example.com'))

    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)

    members = models.ManyToManyField('Membership', related_name='organization_memberships',
                                     verbose_name=_('Members'), blank=True)

    class Meta:
        default_permissions = ()
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @property
    def display(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        if not self.logo:
            return
        if self.logo.width > settings.MAX_ORG_LOGO_SIZE or self.logo.height > settings.MAX_ORG_LOGO_SIZE:
            img = Image.open(self.logo.path)
            img.thumbnail((settings.MAX_ORG_LOGO_SIZE, settings.MAX_ORG_LOGO_SIZE))
            img.save(self.logo.path)

    @property
    def default_membership_type(self) -> MembershipType:
        return self.membership_types.filter(default=True).first()

    @property
    def next_shift(self) -> Optional[Shift]:
        return self.shifts.filter(end__gte=date.today()).order_by('start').first()

    @property
    def future_events(self) -> QuerySet[Event]:
        return self.events.filter(end_date__gte=date.today())

    def get_membership_users(self, membership_types: Optional[QuerySet[MembershipType]] = None) -> QuerySet[User]:
        query = Q()
        if membership_types:
            query = Q(type__in=membership_types)
        user_pks = set()
        for member in self.members.filter(query):
            user_pks.update(member.user_pks)
        from shiftings.accounts.models import User
        return User.objects.filter(pk__in=user_pks)

    def is_member(self, user: User) -> bool:
        if self.all_members.filter(user=user).exists():
            return True
        return user.groups.filter(pk__in=[member.group.pk for member in self.all_members.filter(group__isnull=False)])

    def get_absolute_url(self) -> str:
        return reverse('organization', args=[self.pk])
