from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

from shiftings.utils.fields.date_time import DateField


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

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        if not self.logo:
            return
        if self.logo.width > settings.MAX_EVENT_LOGO_SIZE or self.logo.height > settings.MAX_EVENT_LOGO_SIZE:
            img = Image.open(self.logo.path)
            img.thumbnail((settings.MAX_EVENT_LOGO_SIZE, settings.MAX_EVENT_LOGO_SIZE))
            img.save(self.logo.path)

    def get_absolute_url(self) -> str:
        return reverse('event', args=[self.pk])
