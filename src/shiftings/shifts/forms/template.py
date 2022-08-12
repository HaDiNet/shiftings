from django import forms

from shiftings.shifts.models import ShiftTemplate


class ShiftTemplateForm(forms.ModelForm):
    class Meta:
        model = ShiftTemplate
        fields = ['name', 'shift_type', 'start_delay', 'duration', 'required_users', 'max_users', 'additional_infos']
