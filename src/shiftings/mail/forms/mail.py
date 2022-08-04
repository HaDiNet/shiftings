from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models import MembershipType, Organization


class MailForm(forms.Form):
    subject = forms.CharField(max_length=255, label=_('Subject'))
    text = forms.CharField(label=_('Text'), widget=forms.Textarea)
    attachments = forms.FileField(label=_('Attachments'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].widget.attrs['multiple'] = True


class OrganizationMailForm(MailForm):
    membership_types = forms.ModelMultipleChoiceField(
        queryset=MembershipType.objects.none(), required=False,
        help_text=_('Send the mail only to specific membership types. Or leave blank to send to all.')
    )

    organization: Organization

    def __init__(self, organization: Organization, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

        self.fields['membership_types'].queryset = organization.membership_types
