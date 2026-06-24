from typing import Any

from django import forms
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.shifts.models import Shift


class ExcuseOtherForm(forms.Form):
    user = ModelChoiceField(queryset=User.objects.none(), label=_('User to excuse'))

    shift: Shift

    def __init__(self, shift: Shift, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.shift = shift
        excused_ids = list(shift.excused_users.values_list('pk', flat=True))
        self.fields['user'].queryset = shift.organization.users.exclude(pk__in=excused_ids)
