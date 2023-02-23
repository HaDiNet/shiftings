from typing import Any, Dict

from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import RecurringShift
from shiftings.shifts.models.recurring import ProblemHandling
from shiftings.shifts.utils.time_frame import TimeFrameType


class RecurringShiftForm(forms.ModelForm):
    ordinal = forms.IntegerField(label=_('Ordinal'), min_value=1, max_value=31)

    class Meta:
        model = RecurringShift
        fields = ['name', 'organization', 'time_frame_field', 'ordinal', 'week_day_field', 'month_field',
                  'first_occurrence', 'color', 'template', 'weekend_handling_field', 'weekend_warning',
                  'holiday_handling_field', 'holiday_warning']

    def __init__(self, *args: Any, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['organization'].disabled = True

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        time_frame_type = TimeFrameType(cleaned_data['time_frame_field'])
        if cleaned_data['week_day_field'] is None and time_frame_type in TimeFrameType.get_weekday_types():
            self.add_error('week_day_field', _('Weekday can\'t be empty with the chosen time frame type.'))
        if cleaned_data['month_field'] is None and time_frame_type in TimeFrameType.get_monthday_types():
            self.add_error('month_field', _('Month can\'t be empty with the chosen time frame type.'))
        if cleaned_data['weekend_handling_field'] != ProblemHandling.Ignore and not cleaned_data['weekend_warning']:
            self.add_error('weekend_handling_field', _('You need to add a warning for weekend handling.'))
        if cleaned_data['holiday_handling_field'] != ProblemHandling.Ignore and not cleaned_data['holiday_warning']:
            self.add_error('holiday_handling_field', _('You need to add a warning for holiday handling.'))
        return cleaned_data


class RecurringShiftCreateShiftsForm(forms.Form):
    create_date = forms.DateField()
