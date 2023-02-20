from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import ShiftType


class ShiftTypeForm(forms.ModelForm):
    class Meta:
        model = ShiftType
        fields = ['organization', 'name', 'color']

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields['organization'].disabled = True

    def clean_name(self) -> str:
        name = self.cleaned_data['name']
        if name.lower() == 'system':
            raise ValidationError(_('Can\'t name a shift type "System".'))
        return name
