from tempfile import TemporaryDirectory

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from django.contrib.sessions.middleware import SessionMiddleware

from shiftings.accounts.models import User
from shiftings.utils.views.protected_content import serve_protected


class ProtectedContentViewTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='protected-user', password='secret')

    def _build_request(self):
        request = self.factory.get('/media/protected/file.txt')
        SessionMiddleware(lambda _request: None).process_request(request)
        request.session.save()
        return request

    @override_settings(SERVE_MEDIA_SERVER='nginx')
    def test_serves_nginx_redirect_header_for_unknown_extension(self) -> None:
        with TemporaryDirectory() as media_root:
            request = self._build_request()
            request.user = self.user

            with override_settings(MEDIA_ROOT=media_root):
                response = serve_protected(request, 'protected/file.unknown')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/octet-stream')
        self.assertTrue(response['X-Accel-Redirect'].endswith('/protected/file.unknown'))

    @override_settings(SERVE_MEDIA_SERVER='apache2')
    def test_serves_apache_sendfile_header_for_known_extension(self) -> None:
        with TemporaryDirectory() as media_root:
            request = self._build_request()
            request.user = self.user

            with override_settings(MEDIA_ROOT=media_root):
                response = serve_protected(request, 'protected/file.txt')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertTrue(response['X-SENDFILE'].endswith('/protected/file.txt'))

    @override_settings(SERVE_MEDIA_SERVER='')
    def test_raises_http404_when_server_setting_missing(self) -> None:
        with TemporaryDirectory() as media_root:
            request = self._build_request()
            request.user = self.user

            with override_settings(MEDIA_ROOT=media_root):
                with self.assertRaises(Http404):
                    serve_protected(request, 'protected/file.txt')
