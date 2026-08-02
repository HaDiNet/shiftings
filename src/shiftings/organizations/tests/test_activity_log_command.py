from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization, OrganizationActivityLog


class PruneOrgActivityLogsCommandTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.actor = User.objects.get(username='bob')

    def test_prune_removes_only_entries_older_than_90_days(self) -> None:
        old_entry = OrganizationActivityLog.objects.create(
            organization=self.organization,
            actor=self.actor,
            action=OrganizationActivityLog.Action.ORGANIZATION_UPDATED,
            summary='Old entry',
        )
        recent_entry = OrganizationActivityLog.objects.create(
            organization=self.organization,
            actor=self.actor,
            action=OrganizationActivityLog.Action.ORGANIZATION_UPDATED,
            summary='Recent entry',
        )

        OrganizationActivityLog.objects.filter(pk=old_entry.pk).update(
            created_at=timezone.now() - timedelta(days=91)
        )

        call_command('prune_org_activity_logs')

        self.assertFalse(OrganizationActivityLog.objects.filter(pk=old_entry.pk).exists())
        self.assertTrue(OrganizationActivityLog.objects.filter(pk=recent_entry.pk).exists())
