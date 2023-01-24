from datetime import date, datetime
from typing import Optional

from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import Shift, ShiftTemplate
from shiftings.utils.fields.date_time import TimeField


class ShiftTemplateGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    place = models.CharField(max_length=100, verbose_name=_('Place'), blank=True, null=True)

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     related_name='shift_template_groups', verbose_name=_('Organization'))

    start_time = TimeField(verbose_name=_('Start Time'), db_index=True)

    # shifts: RelatedManager[ShiftTemplate]

    class Meta:
        default_permissions = ()

    @property
    def display(self) -> str:
        return self.name

    def __str__(self):
        return self.display

    def get_shift_objs(self, _date: date, weekend_warning: Optional[str], holiday_warning: Optional[str]) -> list[Shift]:
        start = datetime.combine(_date, self.start_time)
        shifts = []
        for _template in self.shifts.all():
            template: ShiftTemplate = _template
            shifts.append(template.create_shift(start + template.start_delay, weekend_warning, holiday_warning))
        return shifts

    def get_absolute_url(self) -> str:
        return reverse('shift_template_group', args=[self.pk])
