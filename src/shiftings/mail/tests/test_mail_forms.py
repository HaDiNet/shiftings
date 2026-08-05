from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from shiftings.mail.forms.mail import MailForm, OrganizationMailForm, ShiftParticipantMailForm
from shiftings.mail.settings import MAX_ATTACHMENT_SIZE_MB, MAX_TOTAL_ATTACHMENT_SIZE_MB
from shiftings.organizations.models import Organization


class MailFormTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def _mb_file(self, name: str, size_mb: int) -> SimpleUploadedFile:
        return SimpleUploadedFile(name, b'x' * (size_mb * 1024 * 1024))

    def test_single_attachment_size_limit(self) -> None:
        form = MailForm(
            data={'subject': 'Subject', 'text': 'Body'},
            files=MultiValueDict({'attachments': [self._mb_file('too-large.txt', MAX_ATTACHMENT_SIZE_MB + 1)]}),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('attachments', form.errors)

    def test_total_attachment_size_limit(self) -> None:
        half = MAX_TOTAL_ATTACHMENT_SIZE_MB // 2
        form = MailForm(
            data={'subject': 'Subject', 'text': 'Body'},
            files=MultiValueDict({'attachments': [
                self._mb_file('a.txt', half + 1),
                self._mb_file('b.txt', half + 1),
            ]}),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('attachments', form.errors)

    def test_organization_mail_form_uses_organization_membership_types(self) -> None:
        organization = Organization.objects.get(pk=1)

        form = OrganizationMailForm(organization=organization)

        self.assertEqual(
            set(form.fields['membership_types'].queryset.values_list('pk', flat=True)),
            set(organization.membership_types.values_list('pk', flat=True)),
        )


class ShiftParticipantMailFormTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def test_rejects_start_after_end(self) -> None:
        organization = Organization.objects.get(pk=1)
        form = ShiftParticipantMailForm(
            organization=organization,
            data={
                'subject': 'Subject',
                'text': 'Body',
                'start': '2024-01-02 12:00:00',
                'end': '2024-01-01 12:00:00',
                'shift_types': [],
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
