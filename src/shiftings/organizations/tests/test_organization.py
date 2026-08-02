from datetime import datetime
import re

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from shiftings.accounts.models import User
from shiftings.organizations.models import Membership, MembershipType, Organization, OrganizationActivityLog


class OrganizationTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)

    def test_is_admin(self) -> None:
        def is_admin(username: str) -> bool:
            return self.organization.is_admin(User.objects.get(username=username))

        # superuser
        self.assertTrue(is_admin('bob'))
        # staff
        self.assertTrue(is_admin('perry'))
        # organization admin
        self.assertTrue(is_admin('elliot'))
        # organization members
        self.assertFalse(is_admin('jd'))
        self.assertFalse(is_admin('turk'))
        self.assertFalse(is_admin('carla'))
        self.assertFalse(is_admin('janitor'))
        # group
        self.assertFalse(is_admin('gooch'))
        # admin group
        group = Group.objects.create(name='Test')
        jd = User.objects.get(username='jd')
        jd.groups.add(group)
        membership_type = MembershipType.objects.filter(organization=self.organization, admin=True).first()
        Membership.objects.create(organization=self.organization, type=membership_type, group=group)
        self.assertTrue(is_admin('jd'))

    def test_is_member(self) -> None:
        def is_member(username: str) -> bool:
            return self.organization.is_member(User.objects.get(username=username))

        # superuser
        self.assertFalse(is_member('bob'))
        # staff
        self.assertFalse(is_member('perry'))
        # organization admin
        self.assertTrue(is_member('elliot'))
        # organization members
        self.assertTrue(is_member('jd'))
        self.assertTrue(is_member('turk'))
        self.assertTrue(is_member('carla'))
        self.assertTrue(is_member('janitor'))
        # group
        self.assertTrue(is_member('gooch'))


class OrganizationActivityLogAccessTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.org_admin = User.objects.get(username='elliot')
        self.member = User.objects.get(username='jd')

    def test_org_admin_can_access_activity_log_view(self) -> None:
        self.client.force_login(self.org_admin)

        response = self.client.get(reverse('organization_activity_log', args=[self.organization.pk]))

        self.assertEqual(response.status_code, 200)

    def test_non_admin_member_gets_403_on_activity_log_view(self) -> None:
        self.client.force_login(self.member)

        response = self.client.get(reverse('organization_activity_log', args=[self.organization.pk]))

        self.assertEqual(response.status_code, 403)

    def test_activity_log_timestamp_uses_german_format_for_all_locales(self) -> None:
        log_entry = OrganizationActivityLog.objects.create(
            organization=self.organization,
            actor=self.org_admin,
            action=OrganizationActivityLog.Action.ORGANIZATION_UPDATED,
            summary='Timestamp format test',
        )
        OrganizationActivityLog.objects.filter(pk=log_entry.pk).update(created_at=datetime(2026, 4, 5, 14, 30, 0))

        self.client.force_login(self.org_admin)

        with translation.override('en'):
            english_response = self.client.get(reverse('organization_activity_log', args=[self.organization.pk]))
        with translation.override('de'):
            german_response = self.client.get(reverse('organization_activity_log', args=[self.organization.pk]))

        english_content = english_response.content.decode('utf-8', errors='ignore')
        german_content = german_response.content.decode('utf-8', errors='ignore')

        pattern = r'<tbody>.*?<tr>\s*<td>([^<]+)</td>'
        english_match = re.search(pattern, english_content, re.DOTALL)
        german_match = re.search(pattern, german_content, re.DOTALL)

        self.assertIsNotNone(english_match)
        self.assertIsNotNone(german_match)

        english_timestamp = english_match.group(1).strip()
        german_timestamp = german_match.group(1).strip()

        self.assertEqual(english_timestamp, german_timestamp)
        self.assertIn('14:30', english_timestamp)
        self.assertIn('2026', english_timestamp)
