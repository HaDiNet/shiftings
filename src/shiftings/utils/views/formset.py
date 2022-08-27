from abc import ABC
from typing import Any, cast, Dict, Generic, Optional, Type, TypeVar

from django.db import transaction
from django.db.models import Model, QuerySet
from django.forms import BaseModelFormSet
from django.http import HttpRequest, HttpResponse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin

from shiftings.utils.string import not_implemented_text

T = TypeVar('T', bound=Model)


class ModelFormsetBaseView(TemplateResponseMixin, ModelFormMixin, Generic[T], ABC):
    success_url = None
    model_field_name: str
    item_field_name: str

    def get_form_kwargs(self) -> dict[str, Any]:
        return dict()

    def get_form_data(self) -> list[T]:
        return list(self.get_form_queryset())

    # noinspection PyTypeChecker
    def get_form_queryset(self) -> QuerySet[T]:
        raise NotImplementedError(not_implemented_text('get_form_queryset'))

    def get_formset(self, post: Optional[Any] = None) -> Any:
        formset_class = cast(Type[BaseModelFormSet], self.form_class)
        return formset_class(post, initial=self.get_form_data(),
                             form_kwargs=self.get_form_kwargs(),
                             queryset=self.get_form_queryset())

    def get_form(self, *args: Any, **kwargs: Any) -> None:
        return None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        if 'formset' not in context_data:
            if 'formset' in kwargs:
                context_data['formset'] = kwargs['formset']
            else:
                context_data['formset'] = self.get_formset()
        return context_data

    def form_valid(self, formset: BaseModelFormSet) -> HttpResponse:
        raise NotImplementedError(not_implemented_text('form_valid'))

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        formset = self.get_formset(request.POST)
        if formset.is_valid():
            with transaction.atomic():
                return self.form_valid(formset)
        else:
            if not hasattr(self, 'object'):
                setattr(self, 'object', None)
            return self.render_to_response(self.get_context_data(formset=formset))
