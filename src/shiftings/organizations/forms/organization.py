from django.forms import ModelForm

from shiftings.organizations.models import Organization


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'logo', 'email', 'telephone_number', 'website', 'description']
