from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Q, QuerySet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView

from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.forms.shift import ShiftFormSet
from shiftings.shifts.models import Shift
from shiftings.shifts.utils.filter_mixin import ShiftFilterMixin
from shiftings.utils.views.base import BaseLoginMixin
from shiftings.utils.views.formset import ModelFormsetBaseView


class ShiftListView(BaseLoginMixin, ShiftFilterMixin, ListView):
    template_name = 'shifts/shift_list.html'
    model = Shift
    context_object_name = 'shift'
    object: Shift
    paginate_by = 6
    save_path_in_session = True
    title = _('All Shifts')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['add_self_form'] = AddSelfParticipantForm(self.object, initial={'user': self.request.user, })
        return context

    def get_queryset(self) -> QuerySet[Shift]:
        shifts = Shift.objects.filter((Q(event__in=self.request.user.events) |
                                       Q(organization__in=self.request.user.organizations)))
        filter = self.get_filters()
        if 'start_after_field' in self.request.GET:
            shifts = shifts.filter(filter)
        else:
            shifts = shifts.filter(Q(start__date__gte=date.today()) & filter)
        return shifts


class ShiftUpdateMultipleView(BaseLoginMixin, ModelFormsetBaseView[Shift], TemplateView):
    model = Shift
    form_class = ShiftFormSet
    template_name = 'shifts/edit_multiple_shifts.html'
    success_url = reverse_lazy('shift_list')

    def get_object_ids(self) -> list[int]:
        return self.request.GET.getlist('object_id')

    def get_form_queryset(self) -> QuerySet[Shift]:
        return Shift.objects.filter(pk__in=self.get_object_ids())

    def form_valid(self, formset: ShiftFormSet):
        formset.save()
        return self.success

    def has_permission(self):
        return not any(shift.can_edit(self.request.user) for shift in self.get_form_queryset())

    def get_form_data(self) -> list[Shift]:
        return list()
