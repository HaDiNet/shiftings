from django.forms import ModelForm

from shiftings.accounts.models import Membership


class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ['user', 'group']
