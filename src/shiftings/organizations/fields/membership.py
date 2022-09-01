from django import forms
from django.contrib.auth.models import Permission

from shiftings.organizations.models import Membership


class MembershipPermissionField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj: Membership) -> str:
        if not isinstance(obj, Permission):
            return str(obj)
        return str(obj.name)
