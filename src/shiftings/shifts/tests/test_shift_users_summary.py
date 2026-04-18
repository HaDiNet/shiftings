from datetime import datetime, timedelta

from django.test import RequestFactory, TestCase
from django.urls import reverse

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.shifts.models import Participant, Shift
from shiftings.shifts.templatetags.shifts import shift_users_summary


class ShiftUsersSummaryTagTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.organization = Organization.objects.get(pk=1)
        self.org_user = User.objects.get(username='jd')
        self.outsider = User.objects.create_user(username='summary-outsider', password='secret')

        self.shift = Shift.objects.create(
            organization=self.organization,
            name='Summary shift',
            place='Main Hall',
            start=datetime.now() - timedelta(days=1),
            end=datetime.now(),
            required_users=1,
            max_users=4,
        )
        self.shift.participants.add(Participant.objects.create(user=self.org_user))
        self.shift.participants.add(Participant.objects.create(user=self.outsider))

        self.additional_shift = Shift.objects.create(
            organization=self.organization,
            name='Summary shift 2',
            place='Main Hall',
            start=datetime.now() - timedelta(hours=12),
            end=datetime.now() - timedelta(hours=11),
            required_users=1,
            max_users=4,
        )
        self.additional_shift.participants.add(Participant.objects.create(user=self.org_user))

    def test_shift_users_summary_splits_active_and_other_users(self) -> None:
        request = self.factory.get('/')
        request.user = self.org_user

        context = shift_users_summary({'request': request}, self.organization, show_all_users=False, show_future_shifts=True)

        members_by_pk = {member['pk']: member for member in context['members']}
        self.assertIn(self.org_user.pk, members_by_pk)
        self.assertTrue(members_by_pk[self.org_user.pk]['is_org_user'])
        self.assertIn(self.outsider.pk, members_by_pk)
        self.assertFalse(members_by_pk[self.outsider.pk]['is_org_user'])

        totals = [member['total'] for member in context['members']]
        self.assertEqual(totals, sorted(totals, reverse=True))

        self.assertEqual(context['other_participants'], [])

        other_users_by_pk = {member['pk']: member for member in context['other_users']}
        self.assertIn(self.organization.users.exclude(pk=self.org_user.pk).first().pk, other_users_by_pk)

    def test_shift_users_summary_can_filter_to_org_users_only(self) -> None:
        request = self.factory.get('/', {'org_users_only': '1'})
        request.user = self.org_user

        context = shift_users_summary({'request': request}, self.organization, show_all_users=False, show_future_shifts=True)

        member_pks = {member['pk'] for member in context['members']}
        self.assertNotIn(self.outsider.pk, member_pks)
        self.assertIn(self.org_user.pk, member_pks)
        self.assertEqual(context['other_participants'], [])
        self.assertGreater(len(context['other_users']), 0)
        self.assertGreater(context['other_users_count'], 0)

    def test_shift_users_summary_full_summary_has_no_other_users_section(self) -> None:
        request = self.factory.get('/')
        request.user = self.org_user

        context = shift_users_summary({'request': request}, self.organization, show_all_users=True, show_future_shifts=True)

        self.assertTrue(context['show_all_users'])
        self.assertEqual(context['other_participants'], [])
        self.assertEqual(context['other_users'], [])
        self.assertEqual(context['other_users_count'], 0)
        member_pks = {member['pk'] for member in context['members']}
        self.assertIn(self.outsider.pk, member_pks)
        self.assertIn(self.org_user.pk, member_pks)


class OrganizationShiftSummaryViewTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.admin = User.objects.get(username='bob')
        self.client.force_login(self.admin)

    def test_navigation_links_keep_org_users_only_filter(self) -> None:
        response = self.client.get(
            reverse('organization_shift_summary', kwargs={'pk': self.organization.pk}),
            {'org_users_only': '1'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['org_users_only'])
        self.assertIn('org_users_only=1', response.context['previous_url'])
        self.assertIn('org_users_only=1', response.context['next_url'])
