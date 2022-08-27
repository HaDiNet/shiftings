from typing import Any

from django.db.models import QuerySet
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView

from shiftings.shifts.forms.template import ShiftTemplateForm
from shiftings.shifts.models import RecurringShift, ShiftTemplate, ShiftTemplateGroup
from shiftings.utils.views.base import BaseLoginMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView
from shiftings.utils.views.formset import ModelFormsetBaseView


class TemplateGroupListView(BaseLoginMixin, ListView):
    model = ShiftTemplateGroup
    template_name = 'shifts/template/group_list.html'
    context_object_name = 'groups'


class TemplateGroupDetailView(BaseLoginMixin, DetailView):
    model = ShiftTemplateGroup
    template_name = 'shifts/template/group.html'
    context_object_name = 'group'


class TemplateGroupEditView(CreateOrUpdateView, BaseLoginMixin):
    model = ShiftTemplateGroup
    fields = ['name', 'place', 'organization', 'start_time']


ShiftTemplateFormSet = modelformset_factory(ShiftTemplate, ShiftTemplateForm, extra=0, can_delete=True)


class TemplateGroupAddShiftsView(BaseLoginMixin, ModelFormsetBaseView[ShiftTemplate], TemplateView):
    model = ShiftTemplate
    form_class = ShiftTemplateFormSet
    template_name = 'shifts/recurring/templates.html'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['template_group'] = self.get_group()
        return kwargs

    def get_recurring_shift(self) -> RecurringShift:
        return self._get_object(RecurringShift, 'pk')

    def get_group(self) -> ShiftTemplateGroup:
        return self.get_recurring_shift().template

    def get_form_queryset(self) -> QuerySet[ShiftTemplate]:
        return self.get_group().shifts.all()

    def get_form_data(self) -> list[ShiftTemplate]:
        return list()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['recurring_shift'] = self.get_recurring_shift()
        return context

    def form_valid(self, formset: ShiftTemplateFormSet) -> HttpResponse:
        group = self.get_group()
        for form in formset.forms:
            form.instance.group = group
        formset.save()
        return self.success

    def get_success_url(self) -> str:
        return self.get_recurring_shift().get_absolute_url()
