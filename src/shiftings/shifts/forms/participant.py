from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
