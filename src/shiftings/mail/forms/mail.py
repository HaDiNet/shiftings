from typing import Any, Optional

from django import forms
from django.utils.translation import gettext_lazy as _

from shiftings.mail.settings import MAX_ATTACHMENT_SIZE_MB, MAX_TOTAL_ATTACHMENT_SIZE_MB
from shiftings.organizations.models import MembershipType, Organization
from shiftings.shifts.models import ShiftType
from shiftings.utils.fields.date_time import DateTimeFormField


class MailForm(forms.Form):
    subject = forms.CharField(max_length=255, label=_('Subject'))
    text = forms.CharField(label=_('Text'), widget=forms.Textarea)
    attachments = forms.FileField(label=_('Attachments'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].widget.attrs['multiple'] = True
        
    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        attachments = self.files.getlist('attachments')
        for attachment in attachments:
            if attachment.size > MAX_ATTACHMENT_SIZE_MB * 1024 * 1024: # Convert MB to bytes
                self.add_error('attachments', _('Each attachment must be smaller than 10 MB.'))
                break
            
        if sum(attachment.size for attachment in attachments) > MAX_TOTAL_ATTACHMENT_SIZE_MB * 1024 * 1024:
            self.add_error('attachments', _('Total attachment size must be smaller than 25 MB.'))
            
        return cleaned_data


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


class ShiftParticipantMailForm(MailForm):
    shift_types = forms.ModelMultipleChoiceField(
        queryset=ShiftType.objects.none(), required=False,
        help_text=_('Send the mail only to specific shift types. Or leave blank to send to all.')
    )
    start = DateTimeFormField(label=_('Start Time'), required=True)
    end = DateTimeFormField(label=_('End Time'), required=True)

    organization: Organization

    def __init__(self, organization: Organization, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

        self.fields['shift_types'].queryset = organization.shift_types

    def clean(self) -> Optional[dict[str, Any]]:
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if start and end and start > end:
            raise forms.ValidationError(_('Start time must be before end time.'))
        return cleaned_data