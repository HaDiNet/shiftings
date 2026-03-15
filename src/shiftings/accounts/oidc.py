from __future__ import annotations

import re
from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.views import UserModel

from shiftings.accounts.models import User


def populate_user_from_oidc(user_data: dict[str, Any]) -> AbstractUser:
    """Create or update a Django user from OIDC userinfo claims.

    Syncs username, email, groups, and admin status from the OIDC provider.
    """
    username = user_data.get(settings.OAUTH_USERNAME_CLAIM, '')
    groups: list[str] = user_data.get(settings.OAUTH_GROUP_CLAIM, [])
    for group in groups:
        if re.match(settings.OAUTH_GROUP_IGNORE_REGEX, group) is None:
            Group.objects.get_or_create(name=group)
    try:
        user: AbstractUser = User.objects.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        user = User.objects.create(username=username)
        user.set_unusable_password()
        # ignore secondary names
        user.first_name = user_data.get(settings.OAUTH_FIRST_NAME_CLAIM, '').split(' ')[0]
        user.last_name = user_data.get(settings.OAUTH_LAST_NAME_CLAIM, '')
    user.email = user_data.get(settings.OAUTH_EMAIL_CLAIM, '')
    user.groups.set(Group.objects.filter(name__in=groups))

    user.is_superuser = settings.OAUTH_ADMIN_GROUP in groups
    user.is_staff = settings.OAUTH_ADMIN_GROUP in groups
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    user.save()
    return user
