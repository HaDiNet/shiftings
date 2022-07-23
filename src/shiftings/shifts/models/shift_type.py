from __future__ import annotations

from django.db import models
from django.utils.translation import ugettext_lazy as _


class ShiftType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
