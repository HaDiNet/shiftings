from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from shiftings.accounts.models import BaseUser
    from shiftings.shifts.models import Shift


class AttendanceStatus(models.IntegerChoices):
    NONE = 0, _('None')
    PRESENT = 1, _('Present')
    EXCUSED = 2, _('Excused')
    UNEXCUSED = 3, _('Unexcused')


class ShiftAttendanceOverride(models.Model):
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE, related_name='attendance_overrides',
                              verbose_name=_('Shift'))
    user = models.ForeignKey('accounts.BaseUser', on_delete=models.CASCADE,
                             related_name='shift_attendance_overrides', verbose_name=_('User'))
    status = models.PositiveSmallIntegerField(
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.NONE,
        verbose_name=_('Status Override'),
        help_text=_('Override attendance status for this shift')
    )
    points_override = models.DecimalField(
        verbose_name=_('Points Override'),
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Override points awarded for this shift')
    )
    note = models.TextField(verbose_name=_('Shift Attendance Note'), blank=True, default='')

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(fields=['shift', 'user'], name='unique_shift_user_attendance_override')
        ]

    def get_status_display(self) -> str:
        return str(AttendanceStatus(self.status).label)

    def __str__(self) -> str:
        return f'{self.shift} - {self.user.display}: {self.get_status_display()}'
