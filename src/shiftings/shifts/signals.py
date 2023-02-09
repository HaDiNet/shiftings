from typing import Any

from django.db.models import Max
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from shiftings.organizations.models import Organization
from shiftings.shifts.models import ShiftTypeGroup


@receiver(post_save, sender=Organization)
def create_organization_summary_settings(instance: Organization, created: bool, **kwargs: Any) -> None:
    if created:
        from .models import OrganizationSummarySettings
        OrganizationSummarySettings.objects.create(organization=instance)


@receiver(pre_save, sender=ShiftTypeGroup)
def set_order(instance: ShiftTypeGroup, **kwargs: Any) -> None:
    if instance.order is None:
        instance.order = ShiftTypeGroup.objects \
                             .filter(organization=instance.organization) \
                             .aggregate(Max('order'))['order__max'] + 1
