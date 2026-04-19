from typing import Any

from django.db.models import QuerySet
from django.http import HttpResponse
from django.views.generic import DetailView, TemplateView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization import OrganizationMemberMixin, OrganizationPermissionMixin
from shiftings.organizations.views.organization_base import (
    OrganizationCreateUpdateMixin,
    OrganizationMixin,
    OrganizationObjectRedirectMixin,
)
from shiftings.shifts.forms.template import ShiftTemplateFormSet, ShiftTemplateGroupForm
from shiftings.shifts.models import ShiftTemplate, ShiftTemplateGroup
from shiftings.shifts.views.permission import ParticipationPermissionEditView
from shiftings.utils.views.create_update_view import CreateOrUpdateView
from shiftings.utils.views.delete_view import DeleteView
from shiftings.utils.views.formset import ModelFormsetBaseView


class ShiftTemplateGroupMixin(OrganizationMixin):
    model = ShiftTemplateGroup

    def get_organization(self) -> Organization:
        if 'org_pk' in self.kwargs:
            return self._get_object(Organization, 'org_pk')
        if 'pk' in self.kwargs:
            return self._get_object(ShiftTemplateGroup, 'pk').organization
        return self._get_object_from_get(Organization, 'org')


class ShiftTemplateGroupDetailView(OrganizationMemberMixin, ShiftTemplateGroupMixin, DetailView):
    template_name = 'shifts/template/group.html'
    context_object_name = 'group'

    def get_organization(self) -> Organization:
        return self.get_object().organization


class ShiftTemplateGroupEditView(
    ShiftTemplateGroupMixin,
    OrganizationCreateUpdateMixin,
    CreateOrUpdateView,
    OrganizationPermissionMixin,
):
    form_class = ShiftTemplateGroupForm
    permission_required = 'organizations.edit_shift_templates'
    set_organization_initial_on_create_only = False


class ShiftTemplateGroupDeleteView(
    ShiftTemplateGroupMixin,
    OrganizationPermissionMixin,
    OrganizationObjectRedirectMixin,
    DeleteView,
):
    permission_required = 'organizations.edit_shift_templates'


class TemplateGroupAddShiftsView(OrganizationPermissionMixin, ModelFormsetBaseView[ShiftTemplate], TemplateView):
    model = ShiftTemplate
    form_class = ShiftTemplateFormSet
    template_name = 'shifts/edit_templates.html'
    permission_required = 'organizations.edit_shift_templates'

    def get_organization(self) -> Organization:
        return self.get_group().organization

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['template_group'] = self.get_group()
        return kwargs

    def get_group(self) -> ShiftTemplateGroup:
        return self._get_object(ShiftTemplateGroup, 'pk')

    def get_form_queryset(self) -> QuerySet[ShiftTemplate]:
        return self.get_group().shifts.all()

    def get_form_data(self) -> list[ShiftTemplate]:
        return list()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['group'] = self.get_group()
        return context

    def form_valid(self, formset: ShiftTemplateFormSet) -> HttpResponse:
        group = self.get_group()
        for form in formset.forms:
            form.instance.group = group
        formset.save()
        return self.success

    def get_success_url(self) -> str:
        return self.get_group().get_absolute_url()


class TemplateGroupParticipationPermissionEditView(ParticipationPermissionEditView[ShiftTemplateGroup]):
    model = ShiftTemplateGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shift_template = self.get_object()
        context['inherited_permissions'] = shift_template.inherited_participation_permissions \
            .order_by('referred_content_type', 'referred_object_id')
        return context
