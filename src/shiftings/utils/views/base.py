from abc import ABC
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Model
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import ContextMixin

from shiftings.utils.exceptions import Http403
from shiftings.utils.typing import UserRequest

T = TypeVar('T', bound=Model)


class BaseMixin(AccessMixin, ContextMixin, ABC):
    request: HttpRequest
    object: Optional[T] = None

    success_url: Union[str, Callable[..., Any], None] = None
    fail_url: Optional[str] = None
    redirect_url: Optional[str] = None
    save_path_in_session: bool = False
    title: Optional[str] = None

    kwargs: Dict[str, Any]

    def dispatch(self, request, *args, **kwargs):
        if self.save_path_in_session:
            print(request.session.items())
            request.session['saved_path'] = {'title': str(self.get_title()), 'path': request.path, 'params': request.GET}
            print(request.session.items())
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self, **kwargs) -> list[tuple[str, Optional[str]]]:
        if 'saved_path' not in self.request.session:
            return []
        return [(self.request.session['saved_path']['title'],
                 self.request.session['saved_path']['path'] + '?' +
                 urlencode(self.request.session['saved_path']['params'])),
                (self.get_title(), None)]

    def _get_object(self, cls: Type[T], pk_url_kwarg: str) -> T:
        return self._get_object_from_pk(cls, self.kwargs.get(pk_url_kwarg))

    def _get_object_from_get(self, cls: Type[T], pk_get_param: str) -> T:
        param = self.request.GET.get(pk_get_param)
        if param is not None:
            param = int(param)
        return self._get_object_from_pk(cls, param)

    def _get_object_from_pk(self, cls: Type[T], pk: Optional[int]) -> T:
        if self.object and isinstance(self.object, cls):
            if pk is None or pk < 0 or pk == self.object.pk:
                return self.object
        if pk is None:
            raise Http404(_('The pk is missing from the url. This is not supposed to be possible.'))
        obj = cls.objects.filter(pk=pk).first()
        if not obj:
            raise Http404(_('There is no %(name)s with that pk.') % {'name': cls.__name__})
        return obj

    def _handle_no_permission(self) -> Optional[HttpResponse]:
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        if self.redirect_url is not None:
            return HttpResponseRedirect(self.redirect_url)
        raise Http403(_('You don\'t have the required permission.'))

    def get_title(self) -> str:
        return self.title or 'Shiftings'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = self.get_title()
        context_data['breadcrumbs'] = self.get_breadcrumbs()
        return context_data

    def handle_no_permission(self) -> HttpResponse:
        handled = self._handle_no_permission()
        return handled if handled is not None else self.fail

    def get_success_url(self) -> str:
        if self.success_url is None:
            raise ImproperlyConfigured(_('No URL to redirect to. Provide a success_url.'))
        return str(self.success_url)

    @property
    def success(self) -> HttpResponse:
        if 'success_url' in self.request.POST:
            return HttpResponseRedirect(str(self.request.POST['success_url']))
        return HttpResponseRedirect(self.get_success_url())

    def get_fail_url(self) -> Optional[str]:
        return self.fail_url

    @property
    def fail(self) -> HttpResponse:
        url = self.get_fail_url()
        if url is None:
            if self.raise_exception:
                raise PermissionDenied(self.get_permission_denied_message())
            return HttpResponseNotFound(_('Could not find the requested page. This might be a configuration error.'))
        return HttpResponseRedirect(url)


class BaseLoginMixin(LoginRequiredMixin, BaseMixin, ABC):
    request: UserRequest


class BasePermissionMixin(PermissionRequiredMixin, BaseMixin, ABC):
    request: UserRequest
