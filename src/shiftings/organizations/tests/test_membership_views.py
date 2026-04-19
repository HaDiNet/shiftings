from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase
from django.urls import reverse

from shiftings.accounts.models import User
from shiftings.organizations.models import Membership, MembershipType, Organization, OrganizationActivityLog
from shiftings.organizations.views.membership import MembershipAddView
from shiftings.organizations.views.membership_type import MembershipTypeEditView, MembershipTypeRemoveView


class MembershipViewTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.organization = Organization.objects.get(pk=1)
        self.user = User.objects.get(username='elliot')

    def _setup_view(self, view, **kwargs):
        request = self.factory.get('/organizations/test/')
        request.user = self.user
        view.setup(request, **kwargs)
        view.request = request
        view.kwargs = kwargs
        return view

    def test_membership_add_view_resolves_organization_and_redirect(self) -> None:
        view = self._setup_view(MembershipAddView(), org_pk=self.organization.pk)

        self.assertEqual(view.get_organization(), self.organization)
        self.assertEqual(
            view.get_success_url(),
            reverse('organization_admin', args=[self.organization.pk]),
        )

    def test_membership_type_edit_redirects_to_organization_admin(self) -> None:
        view = self._setup_view(MembershipTypeEditView(), org_pk=self.organization.pk)

        self.assertEqual(
            view.get_success_url(),
            reverse('organization_admin', args=[self.organization.pk]),
        )

    def test_membership_type_remove_redirects_to_organization_overview(self) -> None:
        membership_type = MembershipType.objects.filter(organization=self.organization).first()
        self.assertIsNotNone(membership_type)

        view = self._setup_view(
            MembershipTypeRemoveView(),
            org_pk=self.organization.pk,
            member_pk=membership_type.pk,
        )

        self.assertEqual(view.get_success_url(), self.organization.get_absolute_url())


class MembershipEndpointIntegrationTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.admin_user = User.objects.get(username='bob')
        self.target_user = User.objects.get(username='perry')
        self.client.force_login(self.admin_user)

    def test_add_member_endpoint_creates_membership(self) -> None:
        Membership.objects.filter(organization=self.organization, user=self.target_user).delete()
        default_membership_type = self.organization.default_membership_type

        response = self.client.post(
            reverse('membership_add_member', kwargs={'org_pk': self.organization.pk}),
            {
                'organization': self.organization.pk,
                'type': default_membership_type.pk,
                'user': self.target_user.username,
                'group': '',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('organization_admin', args=[self.organization.pk]),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            Membership.objects.filter(
                organization=self.organization,
                type=default_membership_type,
                user=self.target_user,
            ).exists()
        )
        self.assertTrue(
            OrganizationActivityLog.objects.filter(
                organization=self.organization,
                action=OrganizationActivityLog.Action.MEMBERSHIP_ADDED,
            ).exists()
        )

    def test_remove_member_endpoint_deletes_membership_and_sets_success_message(self) -> None:
        default_membership_type = self.organization.default_membership_type
        membership = Membership.objects.create(
            organization=self.organization,
            type=default_membership_type,
            user=self.target_user,
        )

        response = self.client.post(
            reverse(
                'membership_remove',
                kwargs={'org_pk': self.organization.pk, 'member_pk': membership.pk},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Membership.objects.filter(pk=membership.pk).exists())
        self.assertEqual(response.redirect_chain[0][0], reverse('organization_admin', args=[self.organization.pk]))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(str(message) == 'Membership removed' for message in messages))
        self.assertTrue(
            OrganizationActivityLog.objects.filter(
                organization=self.organization,
                action=OrganizationActivityLog.Action.MEMBERSHIP_REMOVED,
            ).exists()
        )
