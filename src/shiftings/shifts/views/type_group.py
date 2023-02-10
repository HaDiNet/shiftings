from typing import Any

from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationAdminMixin
from shiftings.shifts.forms.type_group import ShiftTypeGroupForm
from shiftings.shifts.models import ShiftTypeGroup
from shiftings.utils.views.create_update_view import CreateOrUpdateView
from shiftings.utils.views.delete_view import DeleteView


class ShiftTypeGroupListView(OrganizationAdminMixin, ListView):
    template_name = 'shifts/type_group/list.html'
    model = ShiftTypeGroup
    context_object_name = 'groups'
    permission_required = 'organizations.admin'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'org_pk')

    def get_queryset(self) -> QuerySet:
        return ShiftTypeGroup.objects.filter(organization=self.get_organization())


class ShiftTypeGroupDetailView(OrganizationAdminMixin, DetailView):
    model = ShiftTypeGroup

    object: ShiftTypeGroup

    def get_organization(self) -> Organization:
        return self.object.organization


class ShiftTypeGroupEditView(OrganizationAdminMixin, CreateOrUpdateView[ShiftTypeGroup]):
    model = ShiftTypeGroup
    form_class = ShiftTypeGroupForm

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, 'org_pk')
        return self.get_object().organization

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['organization'] = self.get_organization()
        initial['shift_types'] = self.get_object().shift_types.all()
        return initial

    def form_valid(self, form: ShiftTypeGroupForm) -> HttpResponse:
        if 'shift_types' in form.cleaned_data:
            for shift_type in form.cleaned_data['shift_types']:
                shift_type.group = self.get_object()
                shift_type.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('organization_settings', args=[self.get_organization().pk])


class ShiftTypeGroupRemoveView(OrganizationAdminMixin, DeleteView):
    model = ShiftTypeGroup

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_success_url(self) -> str:
        return reverse('organization_settings', args=[self.get_organization().pk])
