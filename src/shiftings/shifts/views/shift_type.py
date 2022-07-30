from django.urls import reverse_lazy
from django.views.generic import ListView

from shiftings.shifts.models import ShiftType
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftTypeListView(BaseMixin, ListView):
    template_name = 'shifts/type/list.html'
    model = ShiftType
    context_object_name = 'shift_types'


class ShiftTypeEditView(BaseMixin, CreateOrUpdateView):
    model = ShiftType
    fields = ['name']
    success_url = reverse_lazy('shift_types')
