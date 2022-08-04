from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from shiftings.organizations.models import Organization
from shiftings.organizations.models.membership import MembershipType


@receiver(post_save, sender=Organization, dispatch_uid='organization_create_default_membership_types')
def create_default_membership_types(instance: Organization, raw: bool, created: bool, **kwargs: Any) -> None:
    if created and not raw:
        MembershipType.objects.create(organization=instance, name='Manager', admin=True)
        MembershipType.objects.create(organization=instance, name='Member', default=True)
