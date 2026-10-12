from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models.note import OrganizationMemberNote
from shiftings.shifts.models.attendance import ShiftAttendanceOverride


class ShiftAttendanceOverrideForm(forms.ModelForm):
    class Meta:
        model = ShiftAttendanceOverride
        fields = ['status', 'points_override', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['status'].label = _('Attendance Override')
        self.fields['points_override'].label = _('Points Override')
        self.fields['note'].label = _('Shift Note')
        self.fields['points_override'].required = False
        self.fields['note'].required = False


class OrganizationMemberNoteForm(forms.ModelForm):
    class Meta:
        model = OrganizationMemberNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['note'].label = _('Member Note')
        self.fields['note'].required = False
