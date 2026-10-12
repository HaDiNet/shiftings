from decimal import Decimal
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from shiftings.accounts.models import User
from shiftings.organizations.models import Membership, MembershipType, Organization, OrganizationMemberNote
from shiftings.shifts.models import Participant, Shift, ShiftType
from shiftings.shifts.models.attendance import AttendanceStatus, ShiftAttendanceOverride
from shiftings.shifts.utils.scoring import (
    build_attendance_matrix, get_member_shift_attendance, member_score_data
)


class AttendanceTrackingTests(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.summary_settings = self.organization.summary_settings
        self.summary_settings.attendance_points_enabled = True
        self.summary_settings.no_response_penalty = Decimal('0.33')
        self.summary_settings.save()

        self.user_jd = User.objects.get(username='jd')
        self.user_turk = User.objects.get(username='turk')
        self.user_carla = User.objects.get(username='carla')
        self.admin_user = User.objects.get(username='elliot')

        # Add permissions to MembershipType for elliot (admin) and jd (standard member)
        self.admin_type = MembershipType.objects.filter(organization=self.organization, admin=True).first()
        self.member_type = MembershipType.objects.filter(organization=self.organization, default=True).first()

        self.shift_type = ShiftType.objects.create(
            name='Test Mandatory Type',
            organization=self.organization,
            is_mandatory=True,
            point_weight=Decimal('1.00'),
        )

        now = timezone.now()
        self.shift = Shift.objects.create(
            name='Test Shift 1',
            organization=self.organization,
            shift_type=self.shift_type,
            start=now - timedelta(hours=2),
            end=now - timedelta(hours=1),
        )

    def test_original_attendance_states(self) -> None:
        # User JD is a participant (Present)
        participant = Participant.objects.create(user=self.user_jd)
        self.shift.participants.add(participant)

        # User Turk is excused (Excused)
        self.shift.excused_users.add(self.user_turk)

        # User Carla did not respond to mandatory shift (Unexcused)
        rec_jd = get_member_shift_attendance(self.shift, self.user_jd, Decimal('0.33'))
        self.assertEqual(rec_jd['original_status'], AttendanceStatus.PRESENT)
        self.assertEqual(rec_jd['effective_status'], AttendanceStatus.PRESENT)
        self.assertEqual(rec_jd['original_points'], Decimal('1.00'))
        self.assertEqual(rec_jd['effective_points'], Decimal('1.00'))
        self.assertFalse(rec_jd['is_overridden'])
        self.assertEqual(rec_jd['border_class'], 'border-present')
        self.assertEqual(rec_jd['inner_class'], 'inner-present')

        rec_turk = get_member_shift_attendance(self.shift, self.user_turk, Decimal('0.33'))
        self.assertEqual(rec_turk['original_status'], AttendanceStatus.EXCUSED)
        self.assertEqual(rec_turk['effective_status'], AttendanceStatus.EXCUSED)
        self.assertEqual(rec_turk['original_points'], Decimal('0.00'))
        self.assertEqual(rec_turk['border_class'], 'border-excused')
        self.assertEqual(rec_turk['inner_class'], 'inner-excused')

        rec_carla = get_member_shift_attendance(self.shift, self.user_carla, Decimal('0.33'))
        self.assertEqual(rec_carla['original_status'], AttendanceStatus.UNEXCUSED)
        self.assertEqual(rec_carla['effective_status'], AttendanceStatus.UNEXCUSED)
        self.assertEqual(rec_carla['original_points'], Decimal('-0.33'))
        self.assertEqual(rec_carla['border_class'], 'border-unexcused')
        self.assertEqual(rec_carla['inner_class'], 'inner-unexcused')

    def test_attendance_status_and_points_override(self) -> None:
        # Carla was unexcused, override to Present with custom points 2.00
        override = ShiftAttendanceOverride.objects.create(
            shift=self.shift,
            user=self.user_carla,
            status=AttendanceStatus.PRESENT,
            points_override=Decimal('2.00'),
            note='Came later but completed full shift'
        )

        rec = get_member_shift_attendance(self.shift, self.user_carla, Decimal('0.33'), override=override)
        self.assertEqual(rec['original_status'], AttendanceStatus.UNEXCUSED)
        self.assertEqual(rec['effective_status'], AttendanceStatus.PRESENT)
        self.assertEqual(rec['original_points'], Decimal('-0.33'))
        self.assertEqual(rec['effective_points'], Decimal('2.00'))
        self.assertTrue(rec['is_overridden'])
        self.assertTrue(rec['status_overridden'])
        self.assertTrue(rec['points_overridden'])
        self.assertEqual(rec['border_class'], 'border-unexcused')
        self.assertEqual(rec['inner_class'], 'inner-present')
        self.assertEqual(rec['points_display'], '-0.33 -> 2.00')
        self.assertEqual(rec['shift_note'], 'Came later but completed full shift')

    def test_member_score_data_with_overrides(self) -> None:
        # JD participates
        participant = Participant.objects.create(user=self.user_jd)
        self.shift.participants.add(participant)

        # Turk unexcused initially, but overridden to excused
        ShiftAttendanceOverride.objects.create(
            shift=self.shift,
            user=self.user_turk,
            status=AttendanceStatus.EXCUSED,
        )

        data = member_score_data([self.shift], self.user_turk, Decimal('0.33'))
        self.assertEqual(data['attended'], 0)
        self.assertEqual(data['excused'], 1)
        self.assertEqual(data['missed'], 0)
        self.assertEqual(data['score'], Decimal('0.00'))
        self.assertEqual(data['original_score'], Decimal('-0.33'))
        self.assertTrue(data['points_overridden'])

    def test_build_attendance_matrix(self) -> None:
        OrganizationMemberNote.objects.create(
            organization=self.organization,
            user=self.user_jd,
            note='Available on weekends only'
        )

        rows = build_attendance_matrix(
            self.organization,
            [self.shift],
            [self.user_jd, self.user_turk]
        )
        self.assertEqual(len(rows), 2)
        jd_row = next(r for r in rows if r['pk'] == self.user_jd.pk)
        self.assertEqual(jd_row['member_note'], 'Available on weekends only')
        self.assertEqual(len(jd_row['records']), 1)

    def test_overview_view_permissions(self) -> None:
        url = reverse('organization_attendance_overview', args=[self.organization.pk])

        # Anonymous user redirected to login
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Standard user without permission denied (403)
        self.client.force_login(self.user_jd)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Admin user has permission and gets 200
        self.client.force_login(self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shifts/attendance/overview.html')

    def test_overview_view_redirect_when_setting_disabled(self) -> None:
        self.summary_settings.attendance_points_enabled = False
        self.summary_settings.save()

        self.client.force_login(self.admin_user)
        url = reverse('organization_attendance_overview', args=[self.organization.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.organization.get_absolute_url())

    def test_shift_attendance_override_update_view(self) -> None:
        url = reverse('shift_attendance_override_update', args=[self.shift.pk, self.user_turk.pk])

        # Non-admin forbidden
        self.client.force_login(self.user_jd)
        response = self.client.post(url, {
            'status': AttendanceStatus.PRESENT,
            'points_override': '1.50',
            'note': 'Manual check-in'
        })
        self.assertEqual(response.status_code, 403)

        # Admin succeeds
        self.client.force_login(self.admin_user)
        response = self.client.post(url, {
            'status': AttendanceStatus.PRESENT,
            'points_override': '1.50',
            'note': 'Manual check-in',
            'success_url': self.shift.get_absolute_url()
        })
        self.assertEqual(response.status_code, 302)

        override = ShiftAttendanceOverride.objects.get(shift=self.shift, user=self.user_turk)
        self.assertEqual(override.status, AttendanceStatus.PRESENT)
        self.assertEqual(override.points_override, Decimal('1.50'))
        self.assertEqual(override.note, 'Manual check-in')

        # Clearing override deletes it
        response = self.client.post(url, {
            'status': AttendanceStatus.NONE,
            'points_override': '',
            'note': '',
            'success_url': self.shift.get_absolute_url()
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ShiftAttendanceOverride.objects.filter(shift=self.shift, user=self.user_turk).exists())

    def test_organization_member_note_update_view(self) -> None:
        url = reverse('organization_member_note_update', args=[self.organization.pk, self.user_carla.pk])

        # Non-admin forbidden
        self.client.force_login(self.user_jd)
        response = self.client.post(url, {'note': 'Medical leave'})
        self.assertEqual(response.status_code, 403)

        # Admin succeeds
        self.client.force_login(self.admin_user)
        response = self.client.post(url, {'note': 'Medical leave'})
        self.assertEqual(response.status_code, 302)

        note_obj = OrganizationMemberNote.objects.get(organization=self.organization, user=self.user_carla)
        self.assertEqual(note_obj.note, 'Medical leave')

        # Empty note deletes the note object
        response = self.client.post(url, {'note': '   '})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(OrganizationMemberNote.objects.filter(organization=self.organization, user=self.user_carla).exists())
