from django import forms

from shiftings.organizations.models import Membership


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['organization', 'user', 'group']
        widgets = {'organization': forms.HiddenInput()}
