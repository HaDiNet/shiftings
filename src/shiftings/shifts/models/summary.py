from decimal import Decimal

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
    attendance_points_enabled = models.BooleanField(verbose_name=_('Session Points enabled'), default=False,
                                                    help_text=_('Enable per-member Session Points tracking on the '
                                                                'shift summary and the shift detail page.'))
    no_response_penalty = models.DecimalField(verbose_name=_('No-Response Penalty'), max_digits=4, decimal_places=2,
                                              default=Decimal('0.33'),
                                              help_text=_('Points deducted when a member does not respond to a '
                                                          'mandatory shift. Applies organisation-wide.'))

    class Meta:
        default_permissions = ()

    @property
    def default_time_range(self) -> TimeRangeType:
        return TimeRangeType(self.default_time_range_type)

    def __str__(self) -> str:
        return _('Organization summary settings of {organization}').format(organization=self.organization.display)

    def get_absolute_url(self) -> str:
        return reverse('organization_shift_summary', args=[self.organization.pk])
