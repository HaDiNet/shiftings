from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    display_name = models.CharField(max_length=150, verbose_name=_('Display Name'), null=True, blank=True)
    phone_number = PhoneNumberField(verbose_name=_('Telephone Number'), blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['username']

    @property
    def name(self) -> str:
        if self.display_name is None:
            return self.username
        return self.display_name
