from typing import Any, Dict, Generic, Optional, TypeVar

from django.db.models import Model
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

T = TypeVar('T', bound=Model)


class CreateOrUpdateView(TemplateResponseMixin, ModelFormMixin, ProcessFormView, Generic[T]):
    model = T
    request: HttpRequest
    pk_url_kwarg: Optional[str] = 'pk'
    object: Optional[T]

    template_name = 'generic/create_or_update.html'
    form_params: Optional[Dict[str, Any]] = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['is_create'] = self.object is None
        context_data['form_params'] = self.form_params
        context_data['model_name'] = self.model._meta.verbose_name
        return context_data

    def is_create(self) -> bool:
        return self.pk_url_kwarg not in self.kwargs

    def _set_object(self, **kwargs: Any) -> None:
        if self.pk_url_kwarg in kwargs:
            self.object = self.get_object()
        else:
            self.object = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        self._set_object(**kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class CreateView(CreateOrUpdateView):
    pk_url_kwarg = None


class CreateOrUpdateViewWithImageUpload(CreateOrUpdateView):
    form_params: Optional[Dict[str, Any]] = {'enctype': 'multipart/form-data'}
