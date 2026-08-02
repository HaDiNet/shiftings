from django.test import TestCase
from django.urls import reverse

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization


class ShiftTemplateGroupViewTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.admin = User.objects.get(username='bob')

    def test_create_view_uses_org_pk_from_path(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.get(reverse('shift_template_group_create', kwargs={'org_pk': self.organization.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_create'])
        self.assertEqual(response.context['organization'], self.organization)
