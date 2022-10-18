from typing import Any

from django.forms import ModelForm

from shiftings.shifts.models import Shift


class ShiftForm(ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'place', 'organization', 'event', 'shift_type', 'start', 'end', 'required_users',
                  'max_users', 'additional_infos', 'locked']

    def __init__(self, *args: Any, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['organization'].disabled = True
