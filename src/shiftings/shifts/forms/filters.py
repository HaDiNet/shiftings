from django import forms
from django.forms import BooleanField, CheckboxSelectMultiple, ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.events.models import Event
from shiftings.organizations.models import Organization
from shiftings.utils.fields.date_time import DateFormField


class ShiftFilterForm(forms.Form):
    own_shifts_checkbox = BooleanField(widget=forms.CheckboxInput, label=_('Shifts I participate in'), required=False)
    select_org_field = ModelMultipleChoiceField(queryset=Organization.objects.none(), widget=CheckboxSelectMultiple,
                                                required=False)
    select_event_field = ModelMultipleChoiceField(queryset=Event.objects.none(), widget=CheckboxSelectMultiple,
                                                  required=False)
    start_after_field = DateFormField(label=_('Shift starts after'), required=False)
    end_before_field = DateFormField(label=_('Shift ends before'), required=False)

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['select_org_field'].queryset = user.organizations
        self.fields['select_event_field'].queryset = user.events
