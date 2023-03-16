from typing import Any, Optional

from django import forms
from django.core.exceptions import ValidationError
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
    user = forms.CharField(max_length=150, label=_('Username'), required=True)

    class Meta:
        model = Participant
        fields = ['user', 'display_name']

    shift: Shift

    def __init__(self, shift: Shift, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.shift = shift
        self.fields['user'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean_user(self) -> User:
        username = self.cleaned_data.get('user')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise ValidationError(_('The user you entered could not be found.')) from e
        if self.shift.participants.filter(user=user).exists():
            raise ValidationError(_('User {user} is already registered for this shift.').format(user=user))
        return user
