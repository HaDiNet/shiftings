from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from shiftings.accounts.models import User
    from shiftings.organizations.models.organization import Organization


class OrganizationActivityLog(models.Model):
    class Action(models.TextChoices):
        MEMBERSHIP_ADDED = 'membership_added', _('Membership added')
        MEMBERSHIP_REMOVED = 'membership_removed', _('Membership removed')
        MEMBERSHIP_TYPE_CREATED = 'membership_type_created', _('Membership type created')
        MEMBERSHIP_TYPE_UPDATED = 'membership_type_updated', _('Membership type updated')
        MEMBERSHIP_TYPE_REMOVED = 'membership_type_removed', _('Membership type removed')
        ORGANIZATION_UPDATED = 'organization_updated', _('Organization updated')
        SHIFT_CREATED = 'shift_created', _('Shift created')
        SHIFT_UPDATED = 'shift_updated', _('Shift updated')
        SHIFT_REMOVED = 'shift_removed', _('Shift removed')
        SHIFT_PARTICIPANT_ADDED_SELF = 'shift_participant_added_self', _('Shift participant added (self)')
        SHIFT_PARTICIPANT_ADDED_OTHER = 'shift_participant_added_other', _('Shift participant added (other)')
        SHIFT_PARTICIPANT_REMOVED = 'shift_participant_removed', _('Shift participant removed')
        RECURRING_SHIFT_CREATED = 'recurring_shift_created', _('Recurring shift created')
        RECURRING_SHIFT_UPDATED = 'recurring_shift_updated', _('Recurring shift updated')
        RECURRING_SHIFT_REMOVED = 'recurring_shift_removed', _('Recurring shift removed')
        RECURRING_SHIFT_CREATE_SHIFTS = 'recurring_shift_create_shifts', _('Recurring shifts generated')

    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name=_('Organization'),
    )
    actor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='organization_activity_logs',
        verbose_name=_('Actor'),
    )
    action = models.CharField(max_length=64, choices=Action.choices, verbose_name=_('Action'))
    summary = models.CharField(max_length=255, verbose_name=_('Summary'))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_('Metadata'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        default_permissions = ()
        ordering = ['-created_at', '-pk']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['organization', 'action', '-created_at']),
        ]
        verbose_name = _('Organization activity log entry')
        verbose_name_plural = _('Organization activity log entries')

    def __str__(self) -> str:
        return f'[{self.get_action_display()}] {self.summary}'
