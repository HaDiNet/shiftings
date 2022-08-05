from django.urls import reverse_lazy
from django.views.generic import ListView

from shiftings.shifts.models import ShiftGroup
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftGroupListView(BaseMixin, ListView):
    template_name = 'shifts/group/list.html'
    model = ShiftGroup
    context_object_name = 'shift_groups'


class ShiftGroupEditView(BaseMixin, CreateOrUpdateView):
    model = ShiftGroup
    fields = ['name', 'color']
    success_url = reverse_lazy('shift_groups')
