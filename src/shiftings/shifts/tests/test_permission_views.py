from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.shifts.models import ParticipationPermission, ParticipationPermissionType, Shift, ShiftType


class ShiftParticipationPermissionViewTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.shift_type = ShiftType.objects.filter(organization=self.organization).first()
        self.shift = Shift.objects.create(
            organization=self.organization,
            shift_type=self.shift_type,
            name='Permissions integration shift',
            place='K1 Bar',
            start=datetime(2024, 1, 6, 10, 0, 0),
            end=datetime(2024, 1, 6, 12, 0, 0),
            required_users=1,
            max_users=2,
        )
        self.admin = User.objects.get(username='bob')

    def test_get_permissions_page_for_shift(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.get(reverse('shift_part_permissions_edit', kwargs={'pk': self.shift.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.shift)
        self.assertEqual(response.context['organization'], self.organization)

    def test_post_updates_existing_permission_and_redirects(self) -> None:
        content_type = ContentType.objects.get_for_model(self.shift)
        permission = ParticipationPermission.objects.create(
            referred_content_type=content_type,
            referred_object_id=self.shift.pk,
            organization=None,
            permission_type_field=ParticipationPermissionType.Existence,
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('shift_part_permissions_edit', kwargs={'pk': self.shift.pk}),
            {
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '1',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-id': str(permission.pk),
                'form-0-organization': '',
                'form-0-permission_type_field': str(ParticipationPermissionType.Participate.value),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.shift.get_absolute_url())
        permission.refresh_from_db()
        self.assertEqual(permission.permission_type, ParticipationPermissionType.Participate)
