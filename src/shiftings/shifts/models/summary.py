from django.db import models
from django.utils.translation import gettext_lazy as _

from shiftings.utils.time.timerange import TimeRangeType


class OrganizationSummarySettings(models.Model):
    organization = models.OneToOneField('organizations.Organization', on_delete=models.CASCADE,
                                        related_name='summary_settings')
    default_time_range_type = models.PositiveSmallIntegerField(choices=TimeRangeType.choices,
                                                               verbose_name=_('Default time range for summary'),
                                                               default=TimeRangeType.HalfYear)

    @property
    def default_time_range(self) -> TimeRangeType:
        return TimeRangeType(self.default_time_range_type)

    def __str__(self) -> str:
        return _('Organization summary settings of {organization}').format(organization=self.organization.display)
