from typing import Any

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization


@receiver(post_save, sender=User)
def add_permission_fixtures(instance: User, created: bool, raw: bool, **kwargs: Any) -> None:
    if created and raw:
        if instance.username == 'perry':
            content_type = ContentType.objects.get_for_model(Organization)
            instance.user_permissions.add(Permission.objects.get(codename='admin', content_type=content_type))

