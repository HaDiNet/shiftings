from django.core.exceptions import ValidationError
from django.test import TestCase

from shiftings.accounts.models import User
from shiftings.organizations.forms.membership import MembershipForm
from shiftings.organizations.models import Membership, MembershipType, Organization


class MembershipFormTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.admin_user = User.objects.get(username='bob')
        self.member_user = User.objects.get(username='perry')
        self.target_user = User.objects.get(username='carla')
        self.non_admin_user = User.objects.create_user(username='membership-form-user', password='secret')

    def test_non_admin_cannot_select_admin_membership_type(self) -> None:
        form = MembershipForm(
            user=self.non_admin_user,
            initial={'organization': self.organization},
        )

        type_pks = set(form.fields['type'].queryset.values_list('pk', flat=True))
        self.assertNotIn(MembershipType.objects.get(organization=self.organization, admin=True).pk, type_pks)

    def test_clean_user_returns_user_object_for_existing_username(self) -> None:
        form = MembershipForm(
            user=self.admin_user,
            data={
                'organization': self.organization.pk,
                'type': MembershipType.objects.get(organization=self.organization, default=True).pk,
                'user': self.target_user.username,
                'group': '',
            },
            initial={'organization': self.organization},
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['user'], self.target_user)

    def test_clean_user_rejects_unknown_username(self) -> None:
        form = MembershipForm(
            user=self.admin_user,
            data={
                'organization': self.organization.pk,
                'type': MembershipType.objects.get(organization=self.organization, default=True).pk,
                'user': 'missing-user',
                'group': '',
            },
            initial={'organization': self.organization},
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['user'], ['The user you entered could not be found.'])


class MembershipModelConstraintTest(TestCase):
    fixtures = ['user', 'organization']

    def test_membership_requires_user_or_group(self) -> None:
        organization = Organization.objects.get(pk=1)
        membership_type = MembershipType.objects.get(organization=organization, default=True)

        membership = Membership(organization=organization, type=membership_type)

        with self.assertRaises(ValidationError):
            membership.full_clean()