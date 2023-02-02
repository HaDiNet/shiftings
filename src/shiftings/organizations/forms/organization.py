from django.forms import CheckboxSelectMultiple, Form, ModelForm, MultipleChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models import Organization
from shiftings.utils.fields.date_time import DateFormField


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'logo', 'email', 'telephone_number', 'website', 'description']
