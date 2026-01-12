from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import date, time, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

if TYPE_CHECKING:
    from shiftings.events.models import Event
    from shiftings.organizations.models import Organization

REMINDER_TYPES = [
    ('', 'None'),
    ("email", "Email"),
    #("telegram", "Telegram"),
    #('discord', 'Discord'),
    #('whatsapp', 'WhatsApp'),
    #('socket', 'Socket')
]

MIN_TIME=time.fromisoformat('00:00:00')
MAX_TIME=time.fromisoformat('23:59:59,999999')

REMINDER_SUBJECT_MSG='Reminder concerning shift(s) on '

class BaseUser(AbstractUser):
    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.display

    @property
    def display(self) -> str:
        if hasattr(self, 'user'):
            return self.user.display
        return self.get_full_name()


class User(BaseUser):
    display_name = models.CharField(max_length=150, verbose_name=_('Display Name'), null=True, blank=True)
    phone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)
    reminder_type = models.CharField(max_length=32, verbose_name=_('Reminder Type'), default='', blank=True,
        choices=REMINDER_TYPES, help_text='Leave this empty to disable reminders.')
    reminders_days_before_event = models.IntegerField(verbose_name=_('Days before event reminders'), default=1,
        help_text=_('I want to receive reminders this many days before an event.'))

    class Meta:
        default_permissions = ()
        ordering = ['display_name', 'username']

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
        return Event.objects.filter(organization__in=organizations)

    @property
    def shift_count(self) -> int:
        from shiftings.shifts.models import Shift
        total = Shift.objects.filter(participants__user=self).count()
        for claimed_user in self.claimed_org_dummy_users.all():
            total += Shift.objects.filter(participants__user=claimed_user).count()
        return total

    def get_absolute_url(self):
        return reverse('user_profile')
    
    def send_reminders(self):
        from shiftings.shifts.models import Shift
        if self.reminders_days_before_event < 0:
            return
        if self.reminder_type == '':
            return

        reminder_date = date.today() + timedelta(days=self.reminder_emails_days_before_event)

        start_date=datetime.combine(date=reminder_date, time=MIN_TIME)
        shifts = Shift.objects.filter(
            start__date__gte=start_date,
            start__date__lte=datetime.combine(date=reminder_date, time=MAX_TIME),
            participants__user=self
        )

        match self.reminder_type:
            case 'email':
                self.send_reminder_emails(shifts, reminder_date)
            #case 'telegram':
                #self.send_reminder_telegram()
            case _:
                # Do nothing
                return

    def send_reminder_emails(self, shifts, reminder_date):        
        subject = REMINDER_SUBJECT_MSG + reminder_date.__str__()
        text = 'This email is a reminder concerning the following Shiftings '
        if shifts.__len__() > 1:
            text += f'shifts on the {reminder_date.__str__()}: '
            for shift in shifts:
                text += f'\n - {shift.display}: {shift.time_display} for {shift.organization}'
        else:
            shift = shifts[0]
            text += f'shift on the {reminder_date.__str__()}: \n{shift.display}: {shift.time_display} for {shift.organization}'

        email = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL, [self.email], headers={'Reply-To': settings.DEFAULT_FROM_EMAIL})
        email.send()