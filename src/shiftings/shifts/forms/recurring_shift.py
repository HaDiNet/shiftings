from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import RecurringShift


class RecurringShiftForm(forms.ModelForm):
    ordinal = forms.IntegerField(label=_('Ordinal'), min_value=1, max_value=31)

    class Meta:
        model = RecurringShift
        fields = ['name', 'place', 'organization', 'shift_group', 'time_frame_field', 'ordinal', 'week_day_field',
                  'month_field', 'first_occurrence', 'time', 'duration', 'required_users', 'max_users',
                  'additional_infos', 'weekend_handling_field', 'weekend_warning', 'holiday_handling_field',
                  'holiday_warning']
