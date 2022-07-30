from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from shiftings.organizations.models import Organization


@receiver(post_save, sender=Organization)
def create_shopping_cart(instance: Organization, created: bool, **kwargs: Any) -> None:
    if created:
        from .models import OrganizationSummarySettings
        OrganizationSummarySettings.objects.create(organization=instance)
