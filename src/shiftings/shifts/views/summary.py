from django.views.generic import DetailView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.utils.views.base import BaseLoginMixin


class OrganizationShiftSummaryView(OrganizationPermissionMixin, DetailView):
    model = Organization
    template_name = 'shifts/summary/summary.html'
    context_object_name = 'organization'
    permission_required = 'organizations.see_statistics'

    def get_organization(self) -> Organization:
        return self.get_object()
