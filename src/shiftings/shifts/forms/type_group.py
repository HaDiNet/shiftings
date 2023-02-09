from typing import Any

from django import forms

from shiftings.shifts.models import ShiftTypeGroup


class ShiftTypeGroupForm(forms.ModelForm):
    class Meta:
        model = ShiftTypeGroup
        fields = ['organization', 'name', 'default_color']

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields['organization'].disabled = True
