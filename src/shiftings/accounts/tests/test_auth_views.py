import importlib
from json import JSONDecodeError
from unittest.mock import patch

from authlib.integrations.base_client import OAuthError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.test.utils import override_settings
from django.test import RequestFactory
from django.urls import reverse

from shiftings.accounts.models import User


OAUTH_TEST_SETTINGS = {
    'OAUTH_ENABLED': True,
    'OPENID_CONF_URL': 'https://example.invalid/.well-known/openid-configuration',
    'OAUTH_CLIENT_SCOPES': 'openid profile email',
    'OAUTH_USERNAME_CLAIM': 'preferred_username',
    'OAUTH_FIRST_NAME_CLAIM': 'given_name',
    'OAUTH_LAST_NAME_CLAIM': 'family_name',
    'OAUTH_GROUP_CLAIM': 'groups',
    'OAUTH_EMAIL_CLAIM': 'email',
    'OAUTH_ADMIN_GROUP': 'admin',
    'OAUTH_GROUP_IGNORE_REGEX': r'^ignore',
}


def _load_oauth_auth_module():
    module = importlib.reload(importlib.import_module('shiftings.accounts.views.auth'))
    return module


def _attach_session(request) -> None:
    SessionMiddleware(lambda _request: None).process_request(request)
    request.session.save()
    request.user = AnonymousUser()


class UserLoginViewTest(TestCase):
    def test_renders_login_form_by_default_with_single_login_method(self) -> None:
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_form.html')
        self.assertTrue(response.context['local_enabled'])
        self.assertFalse(response.context['ldap_enabled'])
        self.assertFalse(response.context['sso_enabled'])
        self.assertTrue(response.context['is_local'])

    @override_settings(OAUTH_ENABLED=True)
    def test_renders_login_multiple_when_multiple_methods_available(self) -> None:
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_multiple.html')

    def test_renders_login_form_when_login_method_is_provided(self) -> None:
        response = self.client.get(reverse('login'), {'login_method': 'local'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_form.html')

    def test_post_ignores_sso_submit_when_oauth_disabled(self) -> None:
        response = self.client.post(reverse('login'), {'submit': 'sso_login'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_form.html')

    @override_settings(LOCAL_LOGIN_ENABLED=False, LDAP_ENABLED=True, OAUTH_ENABLED=False)
    def test_renders_login_form_when_only_ldap_is_enabled(self) -> None:
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_form.html')
        self.assertFalse(response.context['local_enabled'])
        self.assertTrue(response.context['ldap_enabled'])
        self.assertFalse(response.context['sso_enabled'])

    @override_settings(LOCAL_LOGIN_ENABLED=False, LDAP_ENABLED=False, OAUTH_ENABLED=True)
    def test_renders_login_multiple_when_only_oauth_is_enabled(self) -> None:
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login_multiple.html')


class AuthorizeSSOUserTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='existing-user', password='secret')

    @override_settings(**OAUTH_TEST_SETTINGS)
    def test_post_redirects_to_authorize_when_sso_login_is_requested(self) -> None:
        module = _load_oauth_auth_module()
        self.addCleanup(importlib.reload, module)

        request = self.factory.post(reverse('login'), {'submit': 'sso_login'})
        _attach_session(request)
        request._dont_enforce_csrf_checks = True

        with patch.object(module.UserLoginView, 'get_redirect_url', return_value='/calendar/'), \
                patch.object(module, 'reverse', return_value='/user/auth/'), \
                patch.object(module.oauth.shiftings, 'authorize_redirect', return_value=HttpResponseRedirect('/oauth/')) as authorize_redirect:
            response = module.UserLoginView.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/oauth/')
        authorize_redirect.assert_called_once()
        call_request, redirect_uri = authorize_redirect.call_args.args
        self.assertEqual(call_request.path, reverse('login'))
        self.assertEqual(redirect_uri, 'http://testserver/user/auth/?next=/calendar/')

    @override_settings(**OAUTH_TEST_SETTINGS)
    def test_authenticate_returns_none_for_json_decode_error(self) -> None:
        module = _load_oauth_auth_module()
        self.addCleanup(importlib.reload, module)

        request = self.factory.get(reverse('login'))
        _attach_session(request)

        with patch.object(module.oauth.shiftings, 'authorize_access_token', side_effect=JSONDecodeError('bad', 'doc', 0)):
            user = module.AuthorizeSSOUser().authenticate(request)

        self.assertIsNone(user)

    @override_settings(**OAUTH_TEST_SETTINGS)
    def test_authenticate_populates_new_user_from_userinfo(self) -> None:
        module = _load_oauth_auth_module()
        self.addCleanup(importlib.reload, module)

        request = self.factory.get(reverse('login'))
        _attach_session(request)

        with patch.object(module.oauth.shiftings, 'authorize_access_token', return_value={
            'userinfo': {
                'preferred_username': 'oidc-user',
                'given_name': 'OIDC Example',
                'family_name': 'User',
                'email': 'oidc@example.com',
                'groups': ['admin', 'team-a', 'ignore-me'],
            }
        }):
            user = module.AuthorizeSSOUser().authenticate(request)

        self.assertIsNotNone(user)
        assert user is not None
        user.refresh_from_db()
        self.assertEqual(user.username, 'oidc-user')
        self.assertEqual(user.first_name, 'OIDC')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.email, 'oidc@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(set(user.groups.values_list('name', flat=True)), {'admin', 'team-a'})

    @override_settings(**OAUTH_TEST_SETTINGS)
    def test_get_logs_in_existing_user_and_redirects_next(self) -> None:
        module = _load_oauth_auth_module()
        self.addCleanup(importlib.reload, module)

        request = self.factory.get(reverse('login'), {'next': '/calendar/'})
        _attach_session(request)

        with patch.object(module.AuthorizeSSOUser, 'authenticate', return_value=self.user), \
                patch.object(module, 'login_user') as login_mock, \
                patch.object(module.messages, 'success') as success_mock, \
                patch.object(module.messages, 'error') as error_mock:
            response = module.AuthorizeSSOUser.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/calendar/')
        login_mock.assert_called_once_with(request, self.user)
        success_mock.assert_called_once()
        error_mock.assert_not_called()

    @override_settings(**OAUTH_TEST_SETTINGS)
    def test_get_redirects_to_login_when_authenticate_returns_none(self) -> None:
        module = _load_oauth_auth_module()
        self.addCleanup(importlib.reload, module)

        request = self.factory.get(reverse('login'))
        _attach_session(request)

        with patch.object(module.AuthorizeSSOUser, 'authenticate', return_value=None), \
                patch.object(module.messages, 'error') as error_mock:
            response = module.AuthorizeSSOUser.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        error_mock.assert_called_once()

    @override_settings(**OAUTH_TEST_SETTINGS)
    def test_get_redirects_to_login_on_oauth_error(self) -> None:
        module = _load_oauth_auth_module()
        self.addCleanup(importlib.reload, module)

        request = self.factory.get(reverse('login'))
        _attach_session(request)

        with patch.object(module.AuthorizeSSOUser, 'authenticate', side_effect=OAuthError(error='boom')), \
                patch.object(module.messages, 'error') as error_mock:
            response = module.AuthorizeSSOUser.as_view()(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        error_mock.assert_called_once()


class UserReLoginViewTest(TestCase):
    def test_relogin_logs_out_authenticated_user(self) -> None:
        if not settings.DEBUG:
            self.skipTest('relogin route exists only in DEBUG mode')

        user = User.objects.create_user(username='relogin-user', password='secret')
        self.client.force_login(user)
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('relogin'))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
