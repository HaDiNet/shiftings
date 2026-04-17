from django.test import TestCase
from django.urls import reverse

from shiftings.accounts.models import User


class LandingPageViewTest(TestCase):
    def test_anonymous_user_redirects_to_login(self) -> None:
        response = self.client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_authenticated_user_redirects_to_month_overview(self) -> None:
        user = User.objects.create_user(username='landing-user', password='secret')
        self.client.force_login(user)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('overview_thismonth'))
