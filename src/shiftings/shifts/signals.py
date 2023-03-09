from datetime import timedelta
from typing import Any

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models import Organization
from shiftings.shifts.models import RecurringShift, ShiftTypeGroup


@receiver(post_save, sender=Organization)
def create_organization_summary_settings(instance: Organization, created: bool, **kwargs: Any) -> None:
    if created:
        from .models import OrganizationSummarySettings
        OrganizationSummarySettings.objects.create(organization=instance)


@receiver(pre_save, sender=RecurringShift)
def update_first_occurrence(instance: RecurringShift, **kwargs: Any) -> None:
    for i in range(45):
        if instance.matches_day(instance.first_occurrence + timedelta(days=i)):
            instance.first_occurrence += timedelta(days=i)
            break
    else:
        raise ValueError(_('Could not find a valid first occurrence.'))


@receiver(pre_save, sender=ShiftTypeGroup)
def set_order(instance: ShiftTypeGroup, **kwargs: Any) -> None:
    if instance.order is None:
        instance.order = ShiftTypeGroup.get_next_free_order(instance.organization)
