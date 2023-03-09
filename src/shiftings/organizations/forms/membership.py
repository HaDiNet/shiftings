from typing import Any, Optional

from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.organizations.fields.membership import MembershipPermissionField
from shiftings.organizations.models import Membership, MembershipType


class MembershipForm(forms.ModelForm):
    user = forms.CharField(max_length=150, label=_('Username'), required=False)

    class Meta:
        model = Membership
        fields = ['organization', 'type', 'user', 'group']
        widgets = {'organization': forms.HiddenInput()}

    def __init__(self, user: User, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        organization = self.initial['organization']
        type_filter = Q(organization=organization)
        if not organization.is_admin(user):
            type_filter &= ~Q(admin=True)
        self.fields['type'].queryset = MembershipType.objects.filter(type_filter)
        self.fields['user'].widget.attrs.update({'autofocus': 'autofocus'})
        self.fields['group'].queryset = Group.objects.order_by('name')

    def clean_user(self) -> Optional[User]:
        username = self.cleaned_data.get('user')
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise ValidationError(_('The user you entered could not be found.')) from e
        return user


class MembershipTypeForm(forms.ModelForm):
    permissions = MembershipPermissionField(queryset=Permission.objects.none(), widget=forms.CheckboxSelectMultiple,
                                            required=False)

    class Meta:
        model = MembershipType
        fields = ['organization', 'name', 'permissions']
        widgets = {'organization': forms.HiddenInput()}

    def __init__(self, is_admin: bool, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if is_admin and not self.instance.admin:
            self.fields['permissions'].queryset = Permission.objects.filter(
                content_type=ContentType.objects.get_for_model(MembershipType))
        else:
            self.fields['permissions'].widget = forms.HiddenInput()
            self.fields['permissions'].disabled = True
