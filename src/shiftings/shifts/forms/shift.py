from django.forms import ModelForm

from shiftings.shifts.models import Shift


class ShiftForm(ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'place', 'organization', 'event', 'shift_group', 'start', 'end', 'required_users',
                  'max_users', 'additional_infos', 'locked']
