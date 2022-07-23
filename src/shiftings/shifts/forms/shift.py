from django.forms import ModelForm

from shiftings.shifts.models import Shift


class ShiftForm(ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'shift_type', 'place', 'organization', 'event', 'start', 'end', 'required_shifters',
                  'max_shifters', 'additional_infos', 'locked']
