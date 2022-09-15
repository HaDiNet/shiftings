from typing import Any

from django.db.models import QuerySet
from django.http import HttpResponse
from django.views.generic import TemplateView

from shiftings.organizations.models import Organization
from shiftings.shifts.forms.template import ShiftTemplateFormSet
from shiftings.shifts.models import RecurringShift, ShiftTemplate, ShiftTemplateGroup
from shiftings.utils.views.base import BaseLoginMixin
from shiftings.utils.views.formset import ModelFormsetBaseView
from typing import Any

from django.db.models import QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.organizations.views.organization import OrganizationMemberMixin, OrganizationPermissionMixin
from shiftings.organizations.views.organization_base import OrganizationMixin
from shiftings.shifts.forms.template import ShiftTemplateGroupForm
from shiftings.shifts.models import ShiftTemplateGroup
from shiftings.utils.views.create_update_view import CreateOrUpdateView
from shiftings.utils.views.delete_view import DeleteView


class ShiftTemplateGroupMixin(OrganizationMixin):
    model = ShiftTemplateGroup

    def get_organization(self) -> Organization:
        return self._get_object_from_get(Organization, 'org')


class ShiftTemplateGroupListView(OrganizationMemberMixin, ShiftTemplateGroupMixin, ListView):
    template_name = 'shifts/template/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self) -> QuerySet[ShiftTemplateGroup]:
        return ShiftTemplateGroup.objects.filter(organization=self.get_organization())


class ShiftTemplateGroupDetailView(OrganizationMemberMixin, ShiftTemplateGroupMixin, DetailView):
    template_name = 'shifts/template/group.html'
    context_object_name = 'group'

    def get_organization(self) -> Organization:
        return self.get_object().organization


class ShiftTemplateGroupEditView(ShiftTemplateGroupMixin, CreateOrUpdateView, OrganizationPermissionMixin):
    form_class = ShiftTemplateGroupForm
    permission_required = 'organizations.edit_shift_templates'

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object_from_get(Organization, 'org')
        return self.object.organization

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['organization'] = self.get_organization()
        return initial


class ShiftTemplateGroupDeleteView(ShiftTemplateGroupMixin, OrganizationPermissionMixin, DeleteView):
    permission_required = 'organizations.edit_shift_templates'

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_success_url(self) -> str:
        return reverse('shift_template_groups', args=[self.get_organization().pk])


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
