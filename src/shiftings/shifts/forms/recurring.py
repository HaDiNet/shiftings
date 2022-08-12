from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import RecurringShift
from shiftings.utils.fields.date_time import TimeFormField


class RecurringShiftForm(forms.ModelForm):
    ordinal = forms.IntegerField(label=_('Ordinal'), min_value=1, max_value=31)

    class Meta:
        model = RecurringShift
        fields = ['name', 'organization', 'time_frame_field', 'ordinal', 'week_day_field', 'month_field',
                  'first_occurrence']


class RecurringShiftCreateForm(forms.ModelForm):
    ordinal = forms.IntegerField(label=_('Ordinal'), min_value=1, max_value=31)
    place = forms.CharField(label=_('Place'), max_length=100, required=False)
    start_time = TimeFormField(label=_('Start Time'))

    class Meta:
        model = RecurringShift
        fields = ['name', 'organization', 'place', 'time_frame_field', 'ordinal', 'week_day_field', 'month_field',
                  'first_occurrence', 'start_time']
