from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from shiftings.accounts.models import User


class PasswordResetSecurityViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='reset-user',
            password='old-secret',
            email='reset-user@example.com',
        )
        self.token_generator = PasswordResetTokenGenerator()

    def test_password_reset_confirm_get_with_valid_token_redirects_to_set_password(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = self.token_generator.make_token(self.user)

        response = self.client.get(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))

        self.assertEqual(response.status_code, 302)
        self.assertIn('set-password', response.url)

    def test_password_reset_confirm_post_invalid_data_keeps_password_unchanged(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = self.token_generator.make_token(self.user)
        start_response = self.client.get(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))

        response = self.client.post(
            start_response.url,
            {'new_password1': 'abc', 'new_password2': 'xyz'},
            REMOTE_ADDR='192.0.2.50',
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old-secret'))

    def test_password_reset_confirm_post_success_changes_password(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = self.token_generator.make_token(self.user)
        start_response = self.client.get(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))

        response = self.client.post(
            start_response.url,
            {'new_password1': 'NewS3cure!Passw0rd', 'new_password2': 'NewS3cure!Passw0rd'},
            REMOTE_ADDR='192.0.2.60',
            HTTP_USER_AGENT='pytest-agent',
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_reset_success'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewS3cure!Passw0rd'))
