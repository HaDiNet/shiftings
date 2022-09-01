from django.test import TestCase

from django.contrib.auth.models import Group

from shiftings.accounts.models import User
from shiftings.organizations.models import Membership, MembershipType, Organization


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
