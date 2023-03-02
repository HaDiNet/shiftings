from datetime import timedelta
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import Form, HiddenInput, ModelChoiceField, ModelForm
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Shift, ShiftType
from shiftings.utils.fields.date_time import DateFormField
from shiftings.utils.time.localize import localize_timedelta


class ShiftForm(ModelForm):
    instance: Optional[Shift]

    class Meta:
        model = Shift
        fields = ['name', 'place', 'organization', 'event', 'shift_type', 'start', 'end', 'required_users',
                  'max_users', 'additional_infos', 'locked']

    def __init__(self, *args: Any, instance: Optional[Shift], **kwargs) -> None:
        super().__init__(*args, instance=instance, **kwargs)
        self.fields['organization'].disabled = True
        include_system = False
        if self.instance and self.instance.shift_type and self.instance.shift_type.is_system:
            include_system = True
        organization = instance.organization if instance else self.initial['organization']
        self.fields['shift_type'].queryset = ShiftType.objects.organization(organization, include_system=include_system)

    def clean(self) -> Dict[str, Any]:
        cleaned_data = self.cleaned_data
        max_length = timedelta(minutes=settings.MAX_SHIFT_LENGTH_MINUTES)
        if cleaned_data['end'] - cleaned_data['start'] > max_length:
            self.add_error('end', ValidationError(
                _('Shift is too long, can at most be {max} long').format(max=localize_timedelta(max_length))))
        return cleaned_data


class SelectOrgForm(Form):
    organization = ModelChoiceField(queryset=Organization.objects.none())
    action_date = DateFormField(widget=HiddenInput())

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].queryset = user.organizations
