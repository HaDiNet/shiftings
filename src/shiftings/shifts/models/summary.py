from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.utils.time.timerange import TimeRangeType


class OrganizationSummarySettings(models.Model):
    organization = models.OneToOneField('organizations.Organization', on_delete=models.CASCADE,
                                        related_name='summary_settings')
    other_shifts_group_name = models.CharField(max_length=30, verbose_name=_('"Other" Shift Type Group Name'),
                                               default='Other')
    default_time_range_type = models.PositiveSmallIntegerField(choices=TimeRangeType.choices,
                                                               verbose_name=_('Default time range for summary'),
                                                               default=TimeRangeType.HalfYear)

    class Meta:
        default_permissions = ()

    @property
    def default_time_range(self) -> TimeRangeType:
        return TimeRangeType(self.default_time_range_type)

    def __str__(self) -> str:
        return _('Organization summary settings of {organization}').format(organization=self.organization.display)

    def get_absolute_url(self) -> str:
        return reverse('organization_shift_summary', args = [self.organization.pk])
