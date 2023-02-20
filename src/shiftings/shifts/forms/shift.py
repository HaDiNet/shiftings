from typing import Any, Optional

from django.forms import Form, HiddenInput, ModelChoiceField, ModelForm

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Shift, ShiftType
from shiftings.utils.fields.date_time import DateFormField


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


class SelectOrgForm(Form):
    organization = ModelChoiceField(queryset=Organization.objects.none())
    action_date = DateFormField(widget=HiddenInput())

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].queryset = user.organizations
