from django.views.generic import DetailView

from shiftings.organizations.models import Organization
from shiftings.utils.views.base import BaseLoginMixin


class OrganizationShiftSummaryView(BaseLoginMixin, DetailView):
    model = Organization
    template_name = 'shifts/summary/summary.html'
    context_object_name = 'organization'
