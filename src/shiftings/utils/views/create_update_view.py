from typing import Any, Dict, Optional

from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView


class CreateOrUpdateView(TemplateResponseMixin, ModelFormMixin, ProcessFormView):
    request: HttpRequest
    slug: str = 'pk'
    object: Any

    template_name = 'generic/create_or_update.html'
    form_params: Optional[Dict[str, Any]] = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['is_create'] = self.object is None
        context_data['form_params'] = self.form_params
        context_data['model_name'] = self.model._meta.verbose_name
        return context_data

    def is_create(self) -> bool:
        return self.slug not in self.kwargs

    def _set_object(self, **kwargs: Any) -> None:
        if self.slug in kwargs:
            self.object = self.get_object()
        else:
            self.object = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        self._set_object(**kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class CreateView(CreateOrUpdateView):
    slug = None


class CreateOrUpdateViewWithImageUpload(CreateOrUpdateView):
    form_params: Optional[Dict[str, Any]] = {'enctype': 'multipart/form-data'}
