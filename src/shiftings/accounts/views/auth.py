from __future__ import annotations

from json import JSONDecodeError
from typing import Any, Optional

from authlib.integrations.base_client import OAuthError
from authlib.integrations.django_client import OAuth
from authlib.oauth2 import HttpRequest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as login_user, REDIRECT_FIELD_NAME
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.views import LoginView, LogoutView, UserModel
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from mypyc.codegen.emitmodule import Groups

from shiftings.accounts.models import Shifter


class ShifterLoginView(LoginView):
    redirect_authenticated_user = True
    title = _('Login')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'ldap_enabled': settings.LDAP_ENABLED,
            'sso_enabled': settings.OAUTH_ENABLED,
            'is_local': self.request.GET.get('login_method') is None or self.request.GET.get('login_method') == 'local'
        })
        if self.request.GET.get('login_method') == 'ldap':
            context['login_text'] = _('Login with LDAP Account')
        else:
            context['login_text'] = _('Login with local Account')
        return context

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if self.request.POST.get('submit', '') == 'sso_login':
            redirect_to = self.get_redirect_url()
            redirect_uri = request.build_absolute_uri(reverse('auth'))
            redirect_uri += f'?{REDIRECT_FIELD_NAME}={redirect_to}'
            return oauth.shiftings.authorize_redirect(request, redirect_uri)
        return super().post(request, *args, **kwargs)

    def get_template_names(self) -> list[str]:
        if self.request.GET.get('login_method') is not None or not settings.LDAP_ENABLED and not settings.OAUTH_ENABLED:
            return ['accounts/login_form.html']
        return ['accounts/login_multiple.html']


if settings.OAUTH_ENABLED:
    oauth = OAuth()
    oauth.register(
        name='shiftings',
        server_metadata_url=settings.OPENID_CONF_URL,
        client_kwargs={
            'scope': settings.OAUTH_CLIENT_SCOPES,
        }
    )


    class AuthorizeSSOUser(RedirectView):

        def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            try:
                user = self.authenticate(request)
                if user is None:
                    messages.error(request, _('Error while creating the user instance!'))
                    return HttpResponseRedirect(settings.LOGIN_URL)
                redirect_to = request.GET.get(REDIRECT_FIELD_NAME)
                login_user(self.request, user)
                messages.success(request, _('Successfully logged in!'))
                return HttpResponseRedirect(redirect_to or settings.LOGIN_REDIRECT_URL)
            except OAuthError as e:
                messages.error(request, _('Error while trying to authenticate with sso! %(message)s') % {
                    'message': str(e)
                })
                return HttpResponseRedirect(settings.LOGIN_URL)

        def authenticate(self, request: HttpRequest) -> Optional[AbstractUser]:
            try:
                token = oauth.shiftings.authorize_access_token(request)
                user_data = oauth.shiftings.parse_id_token(request, token)
                if user_data is not None:
                    return self._populate_user(user_data)
            except JSONDecodeError:
                pass
            return None

        @staticmethod
        def _populate_user(user_data: dict[str, Any]) -> AbstractUser:
            username = user_data.get(settings.OAUTH_USERNAME_CLAIM, '')
            groups = user_data.get(settings.OAUTH_GROUP_CLAIM, [])
            try:
                user: AbstractUser = Shifter.objects.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                user = AbstractUser.objects.create(username=username)
                user.set_unusable_password()
            user.first_name = user_data.get(settings.OAUTH_FIRST_NAME_CLAIM, '').split(' ')[0]  # ignore secondary names
            user.last_name = user_data.get(settings.OAUTH_LAST_NAME_CLAIM, '')
            user.room_number = user_data.get(settings.OAUTH_ROOM_NUMBER_CLAIM, '')
            user.email = user_data.get(settings.OAUTH_EMAIL_CLAIM, '')
            user.groups.set(Groups.objects.filter(name__in=groups))

            user.is_superuser = settings.ADMIN_GROUP in groups
            user.is_staff = settings.ADMIN_GROUP in groups
            user.save()
            return user


class ShifterLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    title = _('Logout')
