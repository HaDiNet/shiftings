from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Shifter(AbstractUser):
    display_name = models.CharField(max_length=150, verbose_name=_('Display Name'), null=True, blank=True)
    phone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)

    class Meta:
        default_permissions = ()
