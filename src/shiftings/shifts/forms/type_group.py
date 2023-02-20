from typing import Any

from django import forms

from shiftings.shifts.models import ShiftType, ShiftTypeGroup


class ShiftTypeGroupForm(forms.ModelForm):
    shift_types = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=ShiftType.objects.none(),
                                                 required=False)

    class Meta:
        model = ShiftTypeGroup
        fields = ['organization', 'name']

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fields['organization'].disabled = True
        try:
            self.fields['shift_types'].queryset = ShiftType.objects.filter(organization=self.instance.organization)
        except ShiftTypeGroup.organization.RelatedObjectDoesNotExist:
            pass
