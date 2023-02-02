from django.views.generic import DetailView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.summary import OrganizationShiftSummaryForm
from shiftings.shifts.models import OrganizationSummarySettings
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class OrganizationShiftSummaryView(OrganizationPermissionMixin, DetailView):
    model = Organization
    template_name = 'shifts/summary/summary.html'
    context_object_name = 'organization'
    permission_required = 'organizations.see_statistics'

    def get_organization(self) -> Organization:
        return self.get_object()


class OrganizationEditShiftSummarySettingsView(OrganizationPermissionMixin, CreateOrUpdateView):
    permission_required = 'organizations.edit_organization'
    model = OrganizationSummarySettings
    form_class = OrganizationShiftSummaryForm

    object: OrganizationSummarySettings

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_success_url(self):
        return self.object.get_absolute_url()
