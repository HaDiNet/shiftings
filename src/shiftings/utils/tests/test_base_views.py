from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404, HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from shiftings.accounts.models import User
from shiftings.utils.exceptions import Http403
from shiftings.utils.views.base import BaseMixin


class DummyBaseView(BaseMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('ok')


class NoneHandlingBaseView(DummyBaseView):
    def _handle_no_permission(self):
        return None


class BaseMixinTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='base-user', password='secret')

    def _request(self, path='/', query=None, user=None):
        request = self.factory.get(path, data=query or {})
        SessionMiddleware(lambda _request: None).process_request(request)
        request.session.save()
        request.user = user or AnonymousUser()
        return request

    def _setup_view(self, view, request, **kwargs):
        view.setup(request, **kwargs)
        view.request = request
        view.kwargs = kwargs
        return view

    def test_dispatch_saves_path_in_session_when_enabled(self) -> None:
        request = self._request('/saved-path/', {'page': '2'}, user=self.user)
        view = self._setup_view(DummyBaseView(), request)
        view.save_path_in_session = True
        view.title = 'Saved Title'

        response = view.dispatch(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.session['saved_path']['title'], 'Saved Title')
        self.assertEqual(request.session['saved_path']['path'], '/saved-path/')
        self.assertEqual(request.session['saved_path']['params']['page'], '2')

    def test_get_breadcrumbs_returns_empty_without_saved_path(self) -> None:
        request = self._request('/current/', user=self.user)
        view = self._setup_view(DummyBaseView(), request)

        self.assertEqual(view.get_breadcrumbs(), [])

    def test_get_breadcrumbs_returns_saved_path_and_current_title(self) -> None:
        request = self._request('/current/', user=self.user)
        request.session['saved_path'] = {
            'title': 'Overview',
            'path': '/overview/',
            'params': self.factory.get('/overview/', {'month': '4'}).GET,
        }
        view = self._setup_view(DummyBaseView(), request)
        view.title = 'Current Page'

        breadcrumbs = view.get_breadcrumbs()

        self.assertEqual(breadcrumbs[0][0], 'Overview')
        self.assertTrue(breadcrumbs[0][1].startswith('/overview/?month='))
        self.assertIn('4', breadcrumbs[0][1])
        self.assertEqual(breadcrumbs[1], ('Current Page', None))

    def test_get_object_returns_cached_object_for_none_negative_and_same_pk(self) -> None:
        request = self._request('/object/', user=self.user)
        view = self._setup_view(DummyBaseView(), request)
        view.object = self.user

        self.assertEqual(view._get_object_from_pk(User, None), self.user)
        self.assertEqual(view._get_object_from_pk(User, -1), self.user)
        self.assertEqual(view._get_object_from_pk(User, self.user.pk), self.user)

    def test_get_object_from_pk_raises_for_missing_and_unknown_pk(self) -> None:
        request = self._request('/object/', user=self.user)
        view = self._setup_view(DummyBaseView(), request)

        with self.assertRaises(Http404):
            view._get_object_from_pk(User, None)

        with self.assertRaises(Http404):
            view._get_object_from_pk(User, 999999)

    def test_get_object_and_get_object_from_get_resolve_user(self) -> None:
        request = self._request('/object/', {'user_pk': str(self.user.pk)}, user=self.user)
        view = self._setup_view(DummyBaseView(), request, pk=self.user.pk)

        self.assertEqual(view._get_object(User, 'pk'), self.user)
        self.assertEqual(view._get_object_from_get(User, 'user_pk'), self.user)

    def test_get_context_data_includes_title_and_breadcrumbs(self) -> None:
        request = self._request('/current/', user=self.user)
        request.session['saved_path'] = {
            'title': 'Overview',
            'path': '/overview/',
            'params': self.factory.get('/overview/', {'month': '4'}).GET,
        }
        view = self._setup_view(DummyBaseView(), request)
        view.title = 'Current Page'

        context = view.get_context_data(extra='value')

        self.assertEqual(context['title'], 'Current Page')
        self.assertEqual(context['breadcrumbs'][0][0], 'Overview')
        self.assertTrue(context['breadcrumbs'][0][1].startswith('/overview/?month='))
        self.assertIn('4', context['breadcrumbs'][0][1])
        self.assertEqual(context['extra'], 'value')

    def test_handle_no_permission_redirects_anonymous_users_to_login(self) -> None:
        request = self._request('/needs-login/', {'a': '1'})
        view = self._setup_view(DummyBaseView(), request)

        response = view._handle_no_permission()

        self.assertIsNotNone(response)
        assert response is not None
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)

    def test_handle_no_permission_uses_redirect_url_for_authenticated_user(self) -> None:
        request = self._request('/denied/', user=self.user)
        view = self._setup_view(DummyBaseView(), request)
        view.redirect_url = '/fallback/'

        response = view._handle_no_permission()

        self.assertIsNotNone(response)
        assert response is not None
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/fallback/')

    def test_handle_no_permission_raises_http403_for_authenticated_user(self) -> None:
        request = self._request('/denied/', user=self.user)
        view = self._setup_view(DummyBaseView(), request)

        with self.assertRaises(Http403):
            view._handle_no_permission()

    def test_handle_no_permission_falls_back_to_fail_when_unhandled(self) -> None:
        request = self._request('/denied/', user=self.user)
        view = self._setup_view(NoneHandlingBaseView(), request)
        view.fail_url = '/fail/'

        response = view.handle_no_permission()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/fail/')

    def test_success_url_behaviour(self) -> None:
        request = self.factory.post('/submit/', {'success_url': '/from-post/'})
        SessionMiddleware(lambda _request: None).process_request(request)
        request.session.save()
        request.user = self.user
        view = self._setup_view(DummyBaseView(), request)
        view.success_url = '/from-view/'

        self.assertEqual(view.success.url, '/from-post/')

        request_without_post_url = self.factory.post('/submit/', {})
        SessionMiddleware(lambda _request: None).process_request(request_without_post_url)
        request_without_post_url.session.save()
        request_without_post_url.user = self.user
        view.request = request_without_post_url

        self.assertEqual(view.success.url, '/from-view/')

        view.success_url = None
        with self.assertRaises(ImproperlyConfigured):
            view.get_success_url()

    def test_fail_response_behaviour(self) -> None:
        request = self._request('/denied/', user=self.user)
        view = self._setup_view(DummyBaseView(), request)

        view.fail_url = '/explicit-fail/'
        self.assertEqual(view.fail.url, '/explicit-fail/')

        view.fail_url = None
        view.raise_exception = False
        self.assertEqual(view.fail.status_code, 404)

        view.raise_exception = True
        with self.assertRaises(PermissionDenied):
            _ = view.fail
