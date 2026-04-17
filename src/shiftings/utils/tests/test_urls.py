from __future__ import annotations

from django.conf import settings
from django.test import TestCase
from django.urls import resolve, reverse


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
