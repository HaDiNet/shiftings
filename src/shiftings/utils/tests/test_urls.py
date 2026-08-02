from __future__ import annotations

from datetime import date, datetime

from django.conf import settings
from django.test import TestCase
from django.urls import resolve, reverse

from shiftings.accounts.models import User
from shiftings.organizations.models import OrganizationDummyUser
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Participant, RecurringShift, Shift, ShiftTemplateGroup, ShiftType


class UrlAvailabilityTest(TestCase):
    def assert_url_available(self, name: str, kwargs: dict[str, object] | None = None) -> None:
        kwargs = kwargs or {}
        url = reverse(name, kwargs=kwargs)
        match = resolve(url)
        self.assertEqual(match.url_name, name)

    def test_core_named_urls_are_available(self) -> None:
        cases: list[tuple[str, dict[str, object]]] = [
            ('login', {}),
            ('logout', {}),
            ('user_profile', {}),
            ('user_profile_past', {}),
            ('user_edit_self', {}),
            ('user_theme_preference', {}),
            ('user_delete_self', {}),
            ('password_reset', {}),
            ('password_reset_done', {}),
            ('password_reset_confirm', {'uidb64': 'abc123', 'token': 'set-password-token'}),
            ('password_reset_success', {}),
            ('user_calendar', {}),
            ('user_participation_calendar', {}),
            ('organizations', {}),
            ('organization_create', {}),
            ('own_organizations', {}),
            ('organization', {'pk': 1}),
            ('organization_admin', {'pk': 1}),
            ('organization_settings', {'pk': 1}),
            ('organization_update', {'pk': 1}),
            ('organization_calendar', {'pk': 1}),
            ('org_part_permissions_edit', {'pk': 1}),
            ('claim_user_list', {'org_pk': 1}),
            ('claim_user', {'org_pk': 1, 'pk': 1}),
            ('unclaim_user', {'org_pk': 1, 'pk': 1}),
            ('membership_type_add', {'org_pk': 1}),
            ('membership_type_edit', {'org_pk': 1, 'member_pk': 1}),
            ('membership_type_remove', {'org_pk': 1, 'member_pk': 1}),
            ('membership_add_member', {'org_pk': 1}),
            ('membership_remove', {'org_pk': 1, 'member_pk': 1}),
            ('organization_mail', {'org_pk': 1}),
            ('shift_participants_mail', {'org_pk': 1}),
            ('shift', {'pk': 1}),
            ('shift_create', {'org_pk': 1}),
            ('shift_create_from_template', {'org_pk': 1}),
            ('shift_org_select', {}),
            ('shift_update', {'pk': 1}),
            ('shift_delete', {'pk': 1}),
            ('shift_part_permissions_edit', {'pk': 1}),
            ('add_participant_self', {'pk': 1}),
            ('add_participant_other', {'pk': 1}),
            ('remove_participant', {'pk': 1, 'ppk': 1}),
            ('recurring_shift', {'pk': 1}),
            ('recurring_shift_create', {'org_pk': 1}),
            ('recurring_shift_update', {'pk': 1}),
            ('recurring_shift_delete', {'pk': 1}),
            ('recurring_create_shifts', {'pk': 1}),
            ('organization_shift_summary', {'pk': 1}),
            ('edit_summary_settings', {'pk': 1}),
            ('shift_template_group', {'pk': 1}),
            ('shift_template_group_create', {'org_pk': 1}),
            ('shift_template_group_update', {'pk': 1}),
            ('shift_template_group_delete', {'pk': 1}),
            ('template_group_update_shifts', {'pk': 1}),
            ('template_group_update_permissions', {'pk': 1}),
            ('shift_type_create', {'org_pk': 1}),
            ('shift_type_update', {'pk': 1}),
            ('shift_type_delete', {'pk': 1}),
            ('shift_type_groups', {'org_pk': 1}),
            ('shift_type_group_create', {'org_pk': 1}),
            ('shift_type_group_detail', {'pk': 1}),
            ('shift_type_group_update', {'pk': 1}),
            ('shift_type_group_move_up', {'pk': 1}),
            ('shift_type_group_move_down', {'pk': 1}),
            ('shift_type_group_remove', {'pk': 1}),
            ('overview_today', {}),
            ('overview_day', {'theday': '2026-04-17'}),
            ('overview_today_shift_types', {}),
            ('overview_day_shift_types', {'theday': '2026-04-17'}),
            ('overview_thismonth', {}),
            ('overview_month', {'themonth': '4', 'theyear': '2026'}),
            ('overview_list', {}),
            ('overview_list_shift_types', {}),
            ('set_language', {}),
        ]

        if settings.FEATURES.get('event', False):
            cases.extend([
                ('events', {}),
                ('future_events', {}),
                ('my_events', {}),
                ('my_future_events', {}),
                ('public_events_calendar', {}),
                ('event', {'pk': 1}),
                ('event_create', {'org_pk': 1}),
                ('event_update', {'pk': 1}),
                ('event_calendar', {'pk': 1}),
            ])

        if settings.FEATURES.get('registration', False):
            cases.extend([
                ('register', {}),
                ('confirm_email', {'uidb64': 'abc123', 'token': 'token'}),
            ])

        if settings.OAUTH_ENABLED:
            cases.append(('auth', {}))

        if settings.DEBUG:
            cases.append(('relogin', {}))

        for name, kwargs in cases:
            with self.subTest(name=name):
                self.assert_url_available(name, kwargs)

    def test_critical_urls_have_expected_path_shapes(self) -> None:
        expected_paths: list[tuple[str, dict[str, object], str]] = [
            ('organization_admin', {'pk': 1}, '/organizations/1/admin/'),
            ('organization_settings', {'pk': 1}, '/organizations/1/settings/'),
            ('membership_add_member', {'org_pk': 1}, '/organizations/1/membership/add_member/'),
            ('membership_remove', {'org_pk': 1, 'member_pk': 2}, '/organizations/1/membership/remove/2/'),
            ('membership_type_edit', {'org_pk': 1, 'member_pk': 2}, '/organizations/1/membership/edit_type/2/'),
            ('shift_create', {'org_pk': 1}, '/shifts/create/1'),
            ('shift_update', {'pk': 2}, '/shifts/2/update/'),
            ('shift_delete', {'pk': 2}, '/shifts/2/delete/'),
            ('recurring_shift_create', {'org_pk': 1}, '/shifts/recurring/create/1/'),
            ('recurring_shift_delete', {'pk': 3}, '/shifts/recurring/3/delete/'),
            ('shift_type_create', {'org_pk': 1}, '/shifts/type/create/1/'),
            ('shift_type_delete', {'pk': 3}, '/shifts/type/3/delete/'),
            ('shift_template_group_create', {'org_pk': 1}, '/shifts/template/create/1/'),
            ('shift_type_group_detail', {'pk': 4}, '/shifts/groups/detail/4/'),
            ('shift_type_group_remove', {'pk': 4}, '/shifts/groups/4/remove/'),
            ('overview_day', {'theday': '2026-04-17'}, '/calendar/overview/day/detail/2026-04-17/'),
            ('overview_month', {'themonth': '4', 'theyear': '2026'}, '/calendar/overview/month/4/2026/'),
            ('organization_mail', {'org_pk': 1}, '/organizations/1/mail/'),
            ('shift_participants_mail', {'org_pk': 1}, '/organizations/1/mail/participants'),
        ]

        if settings.FEATURES.get('event', False):
            expected_paths.append(('event_create', {'org_pk': 1}, '/events/create/1/'))

        for name, kwargs, expected_path in expected_paths:
            with self.subTest(name=name):
                self.assertEqual(reverse(name, kwargs=kwargs), expected_path)


class PkUrlRuntimeSmokeTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    MISSING_PK_MESSAGE = 'The pk is missing from the url. This is not supposed to be possible.'

    def setUp(self) -> None:
        self.admin = User.objects.get(username='bob')
        self.client.force_login(self.admin)

        self.organization = Organization.objects.get(pk=1)
        shift_type = ShiftType.objects.filter(organization=self.organization).first()
        self.shift = Shift.objects.create(
            organization=self.organization,
            shift_type=shift_type,
            name='PK URL smoke test shift',
            place='K1 Bar',
            start=datetime(2026, 4, 19, 10, 0, 0),
            end=datetime(2026, 4, 19, 12, 0, 0),
            required_users=1,
            max_users=2,
        )

        self.recurring_shift = RecurringShift.objects.first()
        if self.recurring_shift is None:
            self.recurring_shift = RecurringShift.objects.create(
                name='PK URL smoke test recurring shift',
                organization=self.organization,
                time_frame_field=3,
                ordinal=1,
                week_day_field=6,
                first_occurrence=date.today(),
                template=ShiftTemplateGroup.objects.filter(organization=self.organization).first(),
            )
        self.participant, _ = Participant.objects.get_or_create(
            user=self.admin,
            defaults={'display_name': self.admin.display},
        )
        self.shift.participants.add(self.participant)

        self.dummy_user = OrganizationDummyUser.objects.create_user(
            username='dummy_claim_user',
            password='dummy-password',
            organization_id=1,
        )

    def _assert_pk_url_works(self,
                             *,
                             name: str,
                             kwargs: dict[str, object],
                             method: str = 'get',
                             data: dict[str, object] | None = None) -> None:
        response = getattr(self.client, method)(reverse(name, kwargs=kwargs), data=data or {})
        body = response.content.decode('utf-8', errors='ignore')
        self.assertNotEqual(response.status_code, 404, msg=f'{name} returned 404')
        self.assertNotIn(self.MISSING_PK_MESSAGE, body, msg=f'{name} raised missing-pk error')

    def _assert_cases(self, cases: list[tuple[str, dict[str, object], str, dict[str, object] | None]]) -> None:
        for name, kwargs, method, data in cases:
            with self.subTest(name=name, method=method):
                self._assert_pk_url_works(name=name, kwargs=kwargs, method=method, data=data)

    def test_organization_pk_urls(self) -> None:
        self._assert_cases([
            ('organization', {'pk': 1}, 'get', None),
            ('organization_admin', {'pk': 1}, 'get', None),
            ('organization_settings', {'pk': 1}, 'get', None),
            ('organization_update', {'pk': 1}, 'get', None),
            ('organization_calendar', {'pk': 1}, 'get', None),
            ('org_part_permissions_edit', {'pk': 1}, 'get', None),
            ('organization_shift_summary', {'pk': 1}, 'get', None),
            ('edit_summary_settings', {'pk': 1}, 'get', None),
            ('organization_mail', {'org_pk': 1}, 'get', None),
            ('shift_participants_mail', {'org_pk': 1}, 'get', None),
        ])

    def test_membership_and_claim_pk_urls(self) -> None:
        self._assert_cases([
            ('claim_user_list', {'org_pk': 1}, 'get', None),
            ('claim_user', {'org_pk': 1, 'pk': self.dummy_user.pk}, 'post', None),
            ('unclaim_user', {'org_pk': 1, 'pk': self.dummy_user.pk}, 'post', None),
            ('membership_type_add', {'org_pk': 1}, 'get', None),
            ('membership_type_edit', {'org_pk': 1, 'member_pk': 1}, 'get', None),
            ('membership_type_remove', {'org_pk': 1, 'member_pk': 1}, 'get', None),
            ('membership_add_member', {'org_pk': 1}, 'get', None),
            ('membership_remove', {'org_pk': 1, 'member_pk': 1}, 'post', None),
        ])

    def test_shift_pk_urls(self) -> None:
        self._assert_cases([
            ('shift', {'pk': self.shift.pk}, 'get', None),
            ('shift_create', {'org_pk': 1}, 'get', None),
            ('shift_create_from_template', {'org_pk': 1}, 'get', None),
            ('shift_update', {'pk': self.shift.pk}, 'get', None),
            ('shift_delete', {'pk': self.shift.pk}, 'get', None),
            ('shift_part_permissions_edit', {'pk': self.shift.pk}, 'get', None),
            ('add_participant_self', {'pk': self.shift.pk}, 'get', None),
            ('add_participant_other', {'pk': self.shift.pk}, 'get', None),
            ('remove_participant', {'pk': self.shift.pk, 'ppk': self.participant.pk}, 'post', None),
        ])

    def test_recurring_pk_urls(self) -> None:
        self._assert_cases([
            ('recurring_shift', {'pk': self.recurring_shift.pk}, 'get', None),
            ('recurring_shift_create', {'org_pk': 1}, 'get', None),
            ('recurring_shift_update', {'pk': self.recurring_shift.pk}, 'get', None),
            ('recurring_create_shifts', {'pk': self.recurring_shift.pk}, 'post', {'create_date': date.today().isoformat()}),
            ('recurring_shift_delete', {'pk': self.recurring_shift.pk}, 'post', None),
        ])

    def test_template_and_type_pk_urls(self) -> None:
        self._assert_cases([
            ('shift_template_group', {'pk': 1}, 'get', None),
            ('shift_template_group_create', {'org_pk': 1}, 'get', None),
            ('shift_template_group_update', {'pk': 1}, 'get', None),
            ('shift_template_group_delete', {'pk': 1}, 'get', None),
            ('template_group_update_shifts', {'pk': 1}, 'get', None),
            ('template_group_update_permissions', {'pk': 1}, 'get', None),
            ('shift_type_create', {'org_pk': 1}, 'get', None),
            ('shift_type_update', {'pk': 1}, 'get', None),
            ('shift_type_delete', {'pk': 1}, 'post', None),
            ('shift_type_groups', {'org_pk': 1}, 'get', None),
            ('shift_type_group_create', {'org_pk': 1}, 'get', None),
            ('shift_type_group_update', {'pk': 1}, 'get', None),
            ('shift_type_group_move_up', {'pk': 1}, 'post', None),
            ('shift_type_group_move_down', {'pk': 1}, 'post', None),
            ('shift_type_group_remove', {'pk': 1}, 'post', None),
        ])
