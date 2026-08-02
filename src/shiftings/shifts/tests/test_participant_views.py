from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization, OrganizationActivityLog
from shiftings.shifts.models import Participant, Shift, ShiftType


class ParticipantViewsIntegrationTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.shift_type = ShiftType.objects.filter(organization=self.organization).first()
        self.shift = Shift.objects.create(
            organization=self.organization,
            shift_type=self.shift_type,
            name='Participant integration shift',
            place='K1 Bar',
            start=datetime(2099, 1, 5, 10, 0, 0),
            end=datetime(2099, 1, 5, 12, 0, 0),
            required_users=1,
            max_users=2,
        )
        self.admin = User.objects.get(username='bob')
        self.member = User.objects.get(username='jd')

    def test_add_self_participant_endpoint_adds_current_user(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('add_participant_self', kwargs={'pk': self.shift.pk}),
            {'user': self.admin.pk, 'display_name': ''},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.shift.get_absolute_url())
        self.assertTrue(self.shift.participants.filter(user=self.admin).exists())
        self.assertTrue(
            OrganizationActivityLog.objects.filter(
                organization=self.organization,
                action=OrganizationActivityLog.Action.SHIFT_PARTICIPANT_ADDED_SELF,
            ).exists()
        )

    def test_add_other_participant_with_org_user(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('add_participant_other', kwargs={'pk': self.shift.pk}),
            {'org_user': self.member.pk, 'other_user': '', 'display_name': ''},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.shift.get_absolute_url())
        self.assertTrue(self.shift.participants.filter(user=self.member).exists())
        self.assertTrue(
            OrganizationActivityLog.objects.filter(
                organization=self.organization,
                action=OrganizationActivityLog.Action.SHIFT_PARTICIPANT_ADDED_OTHER,
            ).exists()
        )

    def test_add_other_participant_with_non_member_username(self) -> None:
        outsider = User.objects.create_user(username='outsider-user', password='secret')
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('add_participant_other', kwargs={'pk': self.shift.pk}),
            {'org_user': '', 'other_user': outsider.username, 'display_name': ''},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.shift.get_absolute_url())
        self.assertTrue(self.shift.participants.filter(user=outsider).exists())

    def test_remove_participant_allows_self_removal_and_uses_success_url_override(self) -> None:
        participant = Participant.objects.create(user=self.member, display_name='')
        self.shift.participants.add(participant)
        self.client.force_login(self.member)

        response = self.client.post(
            reverse('remove_participant', kwargs={'pk': self.shift.pk, 'ppk': participant.pk}),
            {'success_url': reverse('user_profile')},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user_profile'))
        self.assertFalse(Participant.objects.filter(pk=participant.pk).exists())
        self.assertTrue(
            OrganizationActivityLog.objects.filter(
                organization=self.organization,
                action=OrganizationActivityLog.Action.SHIFT_PARTICIPANT_REMOVED,
            ).exists()
        )
