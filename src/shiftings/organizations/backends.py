from typing import Optional

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.db.models import Model

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization


class OrganizationPermissionBackend(ModelBackend):
    def has_perm(self, user_obj: User, perm: str, obj: Optional[Model] = None) -> bool:
        if obj is None:
            return False
        if not isinstance(obj, Organization):
            return False
        if obj.is_admin(user_obj):
            return True
        return super().has_perm(user_obj, perm, obj)

    def _collect_permissions(self, user_obj: User, obj: Organization) -> set[str]:
        if user_obj.is_superuser:
            perms = Permission.objects.all()
        else:
            perms = Permission.objects.none()
            for member in obj.members.all():
                if member.is_member(user_obj):
                    perms |= member.type.permissions.all()
        perms = perms.values_list('content_type__app_label', 'codename').order_by()
        return {f'{ct}.{name}' for ct, name in perms}

    def get_all_permissions(self, user_obj: User, obj: Optional[Organization] = None) -> set[str]:
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        if obj is None:
            return super().get_all_permissions(user_obj)
        if not hasattr(user_obj, '_org_perm_cache'):
            user_obj._org_perm_cache = dict()
        if obj.pk not in user_obj._org_perm_cache:
            user_obj._org_perm_cache[obj.pk] = self._collect_permissions(user_obj, obj)
        return user_obj._org_perm_cache[obj.pk]
