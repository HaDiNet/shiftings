from typing import Any, Optional

from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.organizations.models import Membership, MembershipType


class MembershipForm(forms.ModelForm):
    user = forms.CharField(max_length=150, label=_('Username'), required=False)

    class Meta:
        model = Membership
        fields = ['organization', 'type', 'user', 'group']
        widgets = {'organization': forms.HiddenInput()}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['type'].queryset = MembershipType.objects.filter(organization=self.initial['organization'])
        self.fields['user'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean_user(self) -> Optional[User]:
        username = self.cleaned_data.get('user')
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise ValidationError(_('The user you entered could not be found.')) from e
        return user


class MembershipPermissionField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj: Membership) -> str:
        if not isinstance(obj, Permission):
            return str(obj)
        return str(obj.name)


class MembershipPermissionForm(forms.ModelForm):
    permissions = MembershipPermissionField(queryset=Permission.objects.none(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Membership
        fields = ['permissions']
        widgets = {'organization': forms.CheckboxSelectMultiple}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        ctypes = ContentType.objects.filter(app_label='organizations')
        self.fields['permissions'].queryset = Permission.objects.filter(content_type__in=ctypes)


class MembershipTypeForm(forms.ModelForm):
    permissions = MembershipPermissionField(queryset=Permission.objects.none(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = MembershipType
        fields = ['organization', 'name', 'permissions']
        widgets = {'organization': forms.HiddenInput()}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        ctypes = ContentType.objects.filter(app_label='organizations')
        self.fields['permissions'].queryset = Permission.objects.filter(content_type__in=ctypes)
