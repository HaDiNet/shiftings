from datetime import date, timedelta
from typing import Any

from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import DetailView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.summary import OrganizationShiftSummaryForm, SelectSummaryTimeRangeForm
from shiftings.shifts.models import OrganizationSummarySettings
from shiftings.utils.time.timerange import TimeRangeType
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class OrganizationEditShiftSummarySettingsView(OrganizationPermissionMixin, CreateOrUpdateView):
    permission_required = 'organizations.edit_organization'
    model = OrganizationSummarySettings
    form_class = OrganizationShiftSummaryForm

    object: OrganizationSummarySettings

    def get_organization(self) -> Organization:
        return self.get_object().organization

    def get_success_url(self):
        return reverse('organization_settings', args=[self.get_organization()])


class OrganizationShiftSummaryView(OrganizationPermissionMixin, DetailView):
    model = Organization
    template_name = 'shifts/summary/summary.html'
    context_object_name = 'organization'
    permission_required = 'organizations.see_statistics'

    def get_organization(self) -> Organization:
        return self.get_object()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        def get_int(name: str, default: int) -> int:
            try:
                return int(self.request.GET.get(name, default))
            except ValueError:
                return default

        def get_url(_date: date) -> str:
            return reverse('organization_shift_summary', args=[organization.pk]) + '?' + urlencode(
                {'time_range': time_range.value, 'year': _date.year, 'month': _date.month}
            )

        context_data = super().get_context_data(**kwargs)
        organization = self.get_organization()
        try:
            time_range = TimeRangeType(get_int('time_range', organization.summary_settings.default_time_range_type))
        except ValueError:
            time_range = organization.summary_settings.default_time_range
        year = get_int('year', date.today().year)
        month = get_int('month', date.today().month)
        context_data['display'] = time_range.display(year, month)
        start, end = time_range.get_time_range(year, month)
        try:
            previous_date = start - timedelta(days=1)
            context_data['previous_display'] = time_range.display(previous_date.year, previous_date.month)
            context_data['previous_url'] = get_url(previous_date)
        except OverflowError:
            pass
        try:
            next_date = end + timedelta(days=1)
            context_data['next_display'] = time_range.display(next_date.year, next_date.month)
            context_data['next_url'] = get_url(next_date)
        except OverflowError:
            pass
        context_data['select_timerange_form'] = SelectSummaryTimeRangeForm(
            initial={
                'time_range': time_range,
                'year': year,
                'month': month,
            })
        return context_data
