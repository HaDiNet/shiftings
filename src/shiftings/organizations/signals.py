from typing import Any

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from shiftings.organizations.fixtures.permissions import membership_type_permissions
from shiftings.organizations.models import Organization
from shiftings.organizations.models.membership import MembershipType


@receiver(post_save, sender=Organization, dispatch_uid='organization_create_default_membership_types')
def create_default_membership_types(instance: Organization, raw: bool, created: bool, **kwargs: Any) -> None:
    if created and not raw:
        MembershipType.objects.create(organization=instance, name='Manager', admin=True)
        MembershipType.objects.create(organization=instance, name='Member', default=True)


@receiver(post_save, sender=MembershipType, dispatch_uid='organization_add_membership_type_permission_fixtures')
def add_membership_type_permission_fixtures(instance: MembershipType, raw: bool, created: bool, **kwargs: Any) -> None:
    if created and raw:
        if (perms := membership_type_permissions.get(instance.pk)) is not None:
            content_type = ContentType.objects.get_for_model(MembershipType)
            for perm in perms:
                instance.permissions.add(Permission.objects.get(codename=perm, content_type=content_type))
