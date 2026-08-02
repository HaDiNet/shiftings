from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse

from shiftings.accounts.models import User
from shiftings.utils.context_processors import theme as theme_context_processor


class UserThemePreferenceViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='theme-user', password='secret')
        self.url = reverse('user_theme_preference')

    def test_valid_theme_updates_user_and_redirects_to_next(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'theme': User.ThemePreference.DARK, 'next': '/calendar/'})

        self.user.refresh_from_db()
        self.assertEqual(self.user.theme_preference, User.ThemePreference.DARK)
        self.assertRedirects(response, '/calendar/', fetch_redirect_response=False)

    def test_invalid_theme_does_not_update_user_and_redirects_to_next(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'theme': 'invalid', 'next': '/organizations/'})

        self.user.refresh_from_db()
        self.assertEqual(self.user.theme_preference, User.ThemePreference.AUTO)
        self.assertRedirects(response, '/organizations/', fetch_redirect_response=False)

    def test_uses_referer_when_next_is_missing(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'theme': User.ThemePreference.LIGHT}, HTTP_REFERER='/calendar/')

        self.user.refresh_from_db()
        self.assertEqual(self.user.theme_preference, User.ThemePreference.LIGHT)
        self.assertRedirects(response, '/calendar/', fetch_redirect_response=False)

    def test_uses_user_profile_when_next_and_referer_are_missing(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'theme': User.ThemePreference.LIGHT})

        self.assertRedirects(response, reverse('user_profile'))

    def test_requires_login(self) -> None:
        response = self.client.post(self.url, {'theme': User.ThemePreference.DARK})

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])
        self.assertIn('next=', response['Location'])


class ThemeContextProcessorTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_returns_authenticated_user_preference(self) -> None:
        request = self.factory.get('/')
        request.user = User.objects.create_user(username='context-user', password='secret',
                                                theme_preference=User.ThemePreference.DARK)

        context = theme_context_processor(request)

        self.assertEqual(context['theme_preference'], User.ThemePreference.DARK)

    def test_returns_auto_for_unauthenticated_user(self) -> None:
        request = self.factory.get('/')
        request.user = AnonymousUser()

        context = theme_context_processor(request)

        self.assertEqual(context['theme_preference'], User.ThemePreference.AUTO)
