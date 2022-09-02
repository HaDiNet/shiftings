from typing import Any

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from shiftings.accounts.fixtures.permissions import user_permissions
from shiftings.accounts.models import User


@receiver(post_save, sender=User, dispatch_uid='accounts_add_permission_fixtures')
def add_permission_fixtures(instance: User, created: bool, raw: bool, **kwargs: Any) -> None:
    if created and raw:
        if (perms := user_permissions.get(instance.pk)) is not None:
            for perm in perms:
                content_type = ContentType.objects.get_for_model(perm['model'])
                instance.user_permissions.add(Permission.objects.get(codename=perm['name'], content_type=content_type))
