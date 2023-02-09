from typing import Any

from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationAdminMixin
from shiftings.shifts.forms.type import ShiftTypeForm
from shiftings.shifts.models import ShiftType, ShiftTypeGroup
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftTypeGroupListView(OrganizationAdminMixin, ListView):
    template_name = 'shifts/type_group/list.html'
    model = ShiftTypeGroup
    context_object_name = 'groups'
    permission_required = 'organizations.admin'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'org_pk')

    def get_queryset(self) -> QuerySet:
        return ShiftTypeGroup.objects.filter(organization=self.get_organization())

# class ShiftTypeGroupEditView(OrganizationAdminMixin, CreateOrUpdateView[ShiftType]):
#     model = ShiftType
#     form_class = ShiftTypeForm
#     success_url = reverse_lazy('shift_types')
#
#     def get_organization(self) -> Organization:
#         if self.is_create():
#             return self._get_object(Organization, 'org_pk')
#         return self.object.organization
#
#     def get_initial(self) -> dict[str, Any]:
#         initial = super().get_initial()
#         initial['organization'] = self.get_organization()
#         return initial
