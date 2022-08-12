from typing import Any

from django.db.models import QuerySet
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.views.generic import TemplateView

from shiftings.shifts.forms.template import ShiftTemplateForm
from shiftings.shifts.models import RecurringShift, ShiftTemplate, ShiftTemplateGroup
from shiftings.utils.views.base import BaseLoginMixin
from shiftings.utils.views.formset import ModelFormsetBaseView

ShiftTemplateFormSet = modelformset_factory(ShiftTemplate, ShiftTemplateForm, extra=0)


class TemplateGroupAddShiftsView(BaseLoginMixin, ModelFormsetBaseView[ShiftTemplate], TemplateView):
    model = ShiftTemplate
    form_class = ShiftTemplateFormSet
    template_name = 'shifts/recurring/templates.html'

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
            form.instance.save()
        return self.success

    def get_success_url(self) -> str:
        return self.get_recurring_shift().get_absolute_url()
