from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.db.models import Count, F, Q, QuerySet, Sum
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

from shiftings.utils.fields.date_time import DateField

if TYPE_CHECKING:
    from shiftings.accounts.models import User
    from shiftings.shifts.models import Shift


class Event(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     verbose_name=_('Organization'), related_name='events')
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    logo = models.ImageField(verbose_name=_('Logo'), upload_to='upload/events/', blank=True, null=True)

    email = models.EmailField(verbose_name=_('E-Mail'), blank=True, null=True)
    telephone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)
    website = models.URLField(verbose_name=_('Website'), blank=True, null=True)

    start_date = DateField(verbose_name=_('Start Date'), help_text=_('Earliest date where there are shifts available'))
    end_date = DateField(verbose_name=_('End Date'), help_text=_('Latest date where there are shifts available'))

    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)

    allowed_organizations = models.ManyToManyField('organizations.Organization',
                                                   verbose_name=_('Allowed Organizations'),
                                                   help_text=_('Organizations which are allowed to participate'))
    public = models.BooleanField(verbose_name=_('Public'), default=False,
                                 help_text=_('Allow everyone to participate at this event'))

    class Meta:
        default_permissions = ()
        ordering = ['name', 'start_date', 'end_date', 'organization']
        constraints = [
            models.CheckConstraint(name='event_start_after_end',
                                   check=models.Q(start_date__lte=models.F('end_date')))
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def display(self) -> str:
        return _('{name} (by {organization})').format(name=self.name, organization=self.organization.display)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        if not self.logo:
            return
        if self.logo.width > settings.MAX_EVENT_LOGO_SIZE or self.logo.height > settings.MAX_EVENT_LOGO_SIZE:
            img = Image.open(self.logo.path)
            img.thumbnail((settings.MAX_EVENT_LOGO_SIZE, settings.MAX_EVENT_LOGO_SIZE))
            img.save(self.logo.path)

    @property
    def needing_shifts(self) -> QuerySet[Shift]:
        return self.shifts.annotate(user_count=Count('participants')).filter(end__gte=datetime.now(),
                                                                             required_users__gt=F('user_count'))

    @property
    def open_shifts(self) -> QuerySet[Shift]:
        query = Q(end__gte=datetime.now()) & Q(Q(max_users=0) | Q(max_users__gt=F('user_count')))
        return self.shifts.annotate(user_count=Count('participants')).filter(query)

    @property
    def filled_slots(self) -> int:
        return self.shifts.annotate(user_count=Count('participants')).aggregate(Sum('user_count')).get(
            'user_count__sum')

    @property
    def needed_slots(self) -> int:
        return self.shifts.aggregate(Sum('required_users')).get('required_users__sum')

    def can_see(self, user: User) -> bool:
        return self.public or user.events.filter(pk=self.pk).exists()

    def can_participate(self, user: User) -> bool:
        return self.public or any(user.has_perm('organizations.participate_in_shift', org)
                                  for org in self.allowed_organizations.all())

    def get_absolute_url(self) -> str:
        return reverse('event', args=[self.pk])
