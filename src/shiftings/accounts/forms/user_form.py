from typing import Any, Optional

from django import forms
from django.contrib.auth.password_validation import get_password_validators, validate_password
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.settings import AUTH_PASSWORD_VALIDATORS


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label=_('Confirm password'))

    class Meta:
        model = User
        fields = ['username', 'display_name', 'first_name', 'last_name', 'email', 'phone_number',
                  'password', 'confirm_password']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            self.add_error('password', _('Please enter matching passwords'))
            self.add_error('confirm_password', _('Please enter matching passwords'))
        
        # validate password using Django's built-in validators
        try:
            validate_password(password, user=None, password_validators=get_password_validators(AUTH_PASSWORD_VALIDATORS))
        except forms.ValidationError as e:
            self.add_error('password', e)

        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'display_name', 'phone_number']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self.instance, 'ldap_user'):
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            self.fields['email'].required = True
        else:
            self.fields['first_name'].disabled = True
            self.fields['last_name'].disabled = True
            self.fields['email'].disabled = True
            
    def clean(self) -> Optional[dict[str, Any]]:
        cleaned_data = super().clean()
        if hasattr(self.instance, 'ldap_user'):
            # if this is an ldap user, ensure that the fields are not changed
            if (cleaned_data.get('first_name') != self.instance.first_name or
                cleaned_data.get('last_name') != self.instance.last_name or
                cleaned_data.get('email') != self.instance.email):
                raise forms.ValidationError(_('Cannot change first name, last name or email for LDAP users.'))
        return cleaned_data
