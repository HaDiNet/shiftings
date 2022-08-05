from datetime import date
from typing import Any

from django.db.models import Q
from django.views.generic import DetailView

from shiftings.organizations.models import Organization
from shiftings.shifts.models import ShiftGroup
from shiftings.utils.time.timerange import TimeRangeType
from shiftings.utils.views.base import BaseLoginMixin


class OrganizationShiftSummaryView(BaseLoginMixin, DetailView):
    model = Organization
    template_name = 'shifts/summary/summary.html'
    context_object_name = 'organization'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'pk')

    def get_int(self, name: str, default: int) -> int:
        try:
            return int(self.request.GET.get(name, default))
        except ValueError:
            return default

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        org = self.get_organization()
        try:
            time_range_type = TimeRangeType(self.get_int('time_range', org.summary_settings.default_time_range_type))
        except ValueError:
            time_range_type = org.summary_settings.default_time_range
        year = self.get_int('year', date.today().year)
        month = self.get_int('month', date.today().month)
        time_range = time_range_type.get_time_range(year, month)
        time_filter = Q(start__range=time_range) | Q(end__range=time_range)
        groups = list(org.shift_groups.all())
        context['groups'] = groups
        context['has_other'] = org.shifts.filter(time_filter, shift_group__isnull=True).exists()
        context['members'] = [{
            'name': member.user.display,
            'groups': [org.shifts.filter(time_filter, participants__user=member.user,
                                         shift_group__in=group.shift_groups.all()).count()
                       for group in groups],
            'other': org.shifts.filter(time_filter, shift_group__isnull=True, participants__user=member.user).count()
        } for member in org.all_members.all()]
        return context
