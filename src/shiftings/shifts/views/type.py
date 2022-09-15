from typing import Any

from django.urls import reverse_lazy
from django.views.generic import ListView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationAdminMixin
from shiftings.shifts.forms.type import ShiftTypeForm
from shiftings.shifts.models import ShiftType
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftTypeListView(OrganizationAdminMixin, ListView):
    template_name = 'shifts/group/list.html'
    model = ShiftType
    context_object_name = 'shift_types'

    def get_organization(self) -> Organization:
        return self._get_object_from_get(Organization, 'org')


class ShiftTypeEditView(OrganizationAdminMixin, CreateOrUpdateView[ShiftType]):
    model = ShiftType
    form_class = ShiftTypeForm
    success_url = reverse_lazy('shift_types')

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object_from_get(Organization, 'org')
        return self.object.organization

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['organization'] = self.get_organization()
        return initial
