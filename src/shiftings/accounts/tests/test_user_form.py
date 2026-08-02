from django.test import TestCase

from shiftings.accounts.forms.user_form import UserCreateForm, UserUpdateForm
from shiftings.accounts.models import User


class UserCreateFormTest(TestCase):
    def test_valid_passwords_validate(self) -> None:
        form = UserCreateForm(data={
            'username': 'form-user',
            'display_name': 'Form User',
            'first_name': 'Form',
            'last_name': 'User',
            'email': 'form-user@example.com',
            'phone_number': '',
            'password': 'S3cure!Passw0rd',
            'confirm_password': 'S3cure!Passw0rd',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'form-user')

    def test_mismatched_passwords_add_errors_to_both_fields(self) -> None:
        form = UserCreateForm(data={
            'username': 'form-user',
            'display_name': 'Form User',
            'first_name': 'Form',
            'last_name': 'User',
            'email': 'form-user@example.com',
            'phone_number': '',
            'password': 'S3cure!Passw0rd',
            'confirm_password': 'Different!Passw0rd',
        })

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['Please enter matching passwords'])
        self.assertEqual(form.errors['confirm_password'], ['Please enter matching passwords'])

    def test_common_password_is_rejected(self) -> None:
        form = UserCreateForm(data={
            'username': 'form-user',
            'display_name': 'Form User',
            'first_name': 'Form',
            'last_name': 'User',
            'email': 'form-user@example.com',
            'phone_number': '',
            'password': '12345678',
            'confirm_password': '12345678',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class UserUpdateFormTest(TestCase):
    def test_non_ldap_user_has_required_identity_fields(self) -> None:
        user = User.objects.create_user(
            username='update-user',
            password='secret',
            first_name='First',
            last_name='Last',
            email='update@example.com',
        )

        form = UserUpdateForm(instance=user)

        self.assertTrue(form.fields['first_name'].required)
        self.assertTrue(form.fields['last_name'].required)
        self.assertTrue(form.fields['email'].required)

    def test_ldap_user_disables_identity_fields(self) -> None:
        user = User.objects.create_user(
            username='ldap-user',
            password='secret',
            first_name='First',
            last_name='Last',
            email='ldap@example.com',
        )
        user.ldap_user = object()

        form = UserUpdateForm(instance=user)

        self.assertTrue(form.fields['first_name'].disabled)
        self.assertTrue(form.fields['last_name'].disabled)
        self.assertTrue(form.fields['email'].disabled)

    def test_ldap_user_clean_keeps_identity_values(self) -> None:
        user = User.objects.create_user(
            username='ldap-user-clean',
            password='secret',
            first_name='First',
            last_name='Last',
            email='ldap-clean@example.com',
        )
        user.ldap_user = object()

        form = UserUpdateForm(
            instance=user,
            data={
                'first_name': 'Changed',
                'last_name': 'Changed',
                'email': 'changed@example.com',
                'display_name': 'Display',
                'phone_number': '',
            },
        )

        self.assertTrue(form.is_valid())
