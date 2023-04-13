from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.utils.fields.date_time import DateFormField


class SelectDayForm(forms.Form):
    theday = DateFormField(label=_('Select Day'))
