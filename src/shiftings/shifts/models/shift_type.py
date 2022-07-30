from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class ShiftType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'), unique=True)

    class Meta:
        default_permissions = ()
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
