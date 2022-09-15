from typing import Any

from django import forms

from shiftings.shifts.models import ShiftType


class ShiftTypeForm(forms.ModelForm):
    class Meta:
        model = ShiftType
        fields = ['organization', 'name', 'color']

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields['organization'].disabled = True
