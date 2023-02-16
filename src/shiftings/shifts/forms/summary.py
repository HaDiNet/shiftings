from django.forms import ChoiceField, Form, HiddenInput, IntegerField, ModelForm

from shiftings.shifts.models import OrganizationSummarySettings
from shiftings.utils.time.timerange import TimeRangeType


class OrganizationShiftSummaryForm(ModelForm):
    class Meta:
        model = OrganizationSummarySettings
        fields = ['default_time_range_type', 'other_shifts_group_name']


class SelectSummaryTimeRangeForm(Form):
    time_range = ChoiceField(choices=TimeRangeType.choices)
    year = IntegerField(widget=HiddenInput())
    month = IntegerField(widget=HiddenInput())
