from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from shiftings.accounts.models import User
from shiftings.accounts.token import email_confirm_token_generator


class UserRegisterAndConfirmViewTest(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_register_creates_inactive_user_and_sends_confirmation_mail(self) -> None:
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new-user',
                'display_name': 'New User',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'new-user@example.com',
                'phone_number': '',
                'password': 'S3cure!Passw0rd',
                'confirm_password': 'S3cure!Passw0rd',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_profile'), fetch_redirect_response=False)

        user = User.objects.get(username='new-user')
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('new-user@example.com', mail.outbox[0].to)

    def test_confirm_email_with_valid_token_activates_user(self) -> None:
        user = User.objects.create_user(
            username='confirm-user',
            password='secret',
            email='confirm@example.com',
            is_active=False,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_confirm_token_generator.make_token(user)

        response = self.client.get(reverse('confirm_email', kwargs={'uidb64': uidb64, 'token': token}))

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_confirm_email_with_invalid_token_keeps_user_inactive(self) -> None:
        user = User.objects.create_user(
            username='invalid-confirm-user',
            password='secret',
            email='invalid-confirm@example.com',
            is_active=False,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(reverse('confirm_email', kwargs={'uidb64': uidb64, 'token': 'invalid-token'}))

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_confirm_email_with_invalid_uid_renders_page(self) -> None:
        response = self.client.get(reverse('confirm_email', kwargs={'uidb64': 'invalid', 'token': 'token'}))

        self.assertEqual(response.status_code, 200)


class UserDeleteSelfViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='delete-user', password='secret')
        self.url = reverse('user_delete_self')

    def test_delete_requires_confirm_flag(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'confirm': 'false'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_with_confirm_true_removes_user(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'confirm': 'true'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
