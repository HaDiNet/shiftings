from __future__ import annotations

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image


class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), unique=True)
    logo = models.ImageField(verbose_name=_('Logo'), upload_to='upload/organizations/', blank=True, null=True)

    email = models.EmailField(verbose_name=_('E-Mail'), blank=True, null=True)
    telephone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)
    website = models.URLField(verbose_name=_('Website'), blank=True, null=True)

    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)

    managers = models.ManyToManyField('Membership', related_name='managed_organizations',
                                      verbose_name=_('Manager'), blank=True)
    members = models.ManyToManyField('Membership', related_name='organization_memberships',
                                     verbose_name=_('Members'), blank=True)
    helpers = models.ManyToManyField('Membership', related_name='organizations_helper',
                                     verbose_name=_('Helpers'), blank=True)

    class Meta:
        default_permissions = ()
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        if not self.logo:
            return
        if self.logo.width > settings.MAX_ORG_LOGO_SIZE or self.logo.height > settings.MAX_ORG_LOGO_SIZE:
            img = Image.open(self.logo.path)
            img.thumbnail((settings.MAX_ORG_LOGO_SIZE, settings.MAX_ORG_LOGO_SIZE))
            img.save(self.logo.path)

    def get_absolute_url(self) -> str:
        return reverse('organization', args=[self.pk])
