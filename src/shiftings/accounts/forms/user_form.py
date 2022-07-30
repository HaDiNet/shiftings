from typing import Any, Dict

from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User


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
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                _('Please enter matching passwords')
            )
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['display_name', 'first_name', 'last_name', 'email', 'phone_number']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
