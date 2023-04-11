from typing import Any, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.shifts.models import Participant, Shift


class AddSelfParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['user', 'display_name']
        widgets = {'user': forms.HiddenInput()}

    shift: Shift

    def __init__(self, shift: Shift, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.shift = shift
        self.fields['display_name'].widget.attrs.update({'placeholder': self.initial['user'].display})

    def clean(self):
        user = self.cleaned_data['user']
        if self.shift.participants.filter(user=user).exists():
            raise ValidationError(_('User {user} is already registered for this shift.').format(user=user))


class AddOtherParticipantForm(forms.ModelForm):
    org_user = ModelChoiceField(queryset=User.objects.none(), label=_("Organization Users"), required=False)
    other_user = forms.CharField(max_length=150, label=_('Other Users'), required=False,
                                 help_text=_('To add users that do not belong to your organization '
                                             'please enter their username.'))
    user = ModelChoiceField(queryset=User.objects.none(), widget=forms.HiddenInput, required=False)

    class Meta:
        model = Participant
        fields = ['user', 'display_name']

    shift: Shift

    def __init__(self, shift: Shift, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.shift = shift
        self.fields['other_user'].widget.attrs.update({'autofocus': 'autofocus'})
        self.fields['org_user'].queryset = shift.organization.users

    def clean_other_user(self) -> Optional[User]:
        username = self.cleaned_data.get('user')
        if username is None:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise ValidationError(_('The user you entered could not be found.')) from e
        if self.shift.participants.filter(user=user).exists():
            raise ValidationError(_('User {user} is already registered for this shift.').format(user=user))
        return user

    def clean(self) -> Optional[dict[str, Any]]:
        cleaned_data = self.cleaned_data
        cleaned_data['user'] = None
        if cleaned_data.get('other_user') is None and cleaned_data.get('org_user') is None:
            raise ValidationError(_('One of the user fields is required!'))
        elif cleaned_data.get('org_user') is not None:
            cleaned_data['user'] = cleaned_data.get('org_user')
        elif cleaned_data.get('other_user') is not None:
            cleaned_data['user'] = cleaned_data.get('other_user')
        else:
            raise ValidationError(_('Only select one type of user!'))
        if self.shift.is_participant(cleaned_data['user']):
            raise ValidationError(_('Cannot add {user} multiple times to this shift').format(user=cleaned_data['user']))
        return cleaned_data
