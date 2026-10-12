from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView

from shiftings.accounts.models import BaseUser
from shiftings.organizations.models import Organization
from shiftings.organizations.models.note import OrganizationMemberNote
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.attendance import OrganizationMemberNoteForm, ShiftAttendanceOverrideForm
from shiftings.shifts.forms.summary import SelectSummaryTimeRangeForm
from shiftings.shifts.models import Shift
from shiftings.shifts.models.attendance import AttendanceStatus, ShiftAttendanceOverride
from shiftings.shifts.utils.scoring import build_attendance_matrix
from shiftings.utils.time.timerange import TimeRangeType


class OrganizationAttendanceOverviewView(OrganizationPermissionMixin, DetailView):
    model = Organization
    template_name = 'shifts/attendance/overview.html'
    context_object_name = 'organization'
    permission_required = 'organizations.see_attendance_overview'

    def get_organization(self) -> Organization:
        return self.get_object()

    def get(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponse:
        organization = self.get_organization()
        if not getattr(organization.summary_settings, 'attendance_points_enabled', False):
            messages.warning(request, _('Session Points and attendance tracking are not enabled for this organization.'))
            return HttpResponseRedirect(organization.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        def get_int(name: str, default: int) -> int:
            try:
                return int(self.request.GET.get(name, default))
            except ValueError:
                return default

        def get_url(_date: date) -> str:
            return reverse('organization_attendance_overview', args=[organization.pk]) + '?' + urlencode(
                {'time_range': time_range.value, 'year': _date.year, 'month': _date.month}
            )

        context_data = super().get_context_data(**kwargs)
        organization = self.get_organization()
        summary_settings = getattr(organization, 'summary_settings', None)
        try:
            default_range = getattr(summary_settings, 'default_time_range_type', TimeRangeType.HalfYear)
            time_range = TimeRangeType(get_int('time_range', default_range))
        except (ValueError, TypeError):
            time_range = getattr(summary_settings, 'default_time_range', TimeRangeType.HalfYear)
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
            }
        )

        time_filter = Q(start__range=(start, end)) | Q(end__range=(start, end))
        shifts = list(
            organization.shifts.filter(time_filter)
                               .order_by('start', 'name')
                               .select_related('shift_type')
                               .prefetch_related('participants__user', 'excused_users', 'attendance_overrides')
        )

        users = list(organization.users.order_by('username'))
        matrix_rows = build_attendance_matrix(organization, shifts, users)

        can_override = self.request.user.has_perm('organizations.override_attendance', organization)

        context_data.update({
            'shifts': shifts,
            'matrix_rows': matrix_rows,
            'can_override': can_override,
            'attendance_statuses': AttendanceStatus.choices,
        })
        return context_data


class ShiftAttendanceOverrideUpdateView(OrganizationPermissionMixin, View):
    """Create, update, or clear a shift attendance override for a member."""

    http_method_names = ['post']
    permission_required = 'organizations.override_attendance'

    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def get_organization(self) -> Organization:
        return self.get_shift().organization

    def post(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponse:
        shift = self.get_shift()
        user_pk = kwargs.get('user_pk')
        user = get_object_or_404(BaseUser, pk=user_pk)

        override, _created = ShiftAttendanceOverride.objects.get_or_create(
            shift=shift,
            user=user,
            defaults={'status': AttendanceStatus.NONE, 'note': ''}
        )

        form = ShiftAttendanceOverrideForm(request.POST, instance=override)
        if form.is_valid():
            cleaned_status = form.cleaned_data.get('status', AttendanceStatus.NONE)
            cleaned_points = form.cleaned_data.get('points_override')
            cleaned_note = form.cleaned_data.get('note', '')

            # If all override fields are cleared, delete the override record
            if (cleaned_status == AttendanceStatus.NONE
                    and cleaned_points is None
                    and not cleaned_note):
                override.delete()
                messages.success(request, _('Attendance override cleared for {user}.').format(user=user.display))
            else:
                form.save()
                messages.success(request, _('Attendance override updated for {user}.').format(user=user.display))
        else:
            messages.error(request, _('Failed to update attendance override: {errors}').format(errors=form.errors))

        success_url = request.POST.get('success_url')
        if success_url:
            return HttpResponseRedirect(str(success_url))
        return HttpResponseRedirect(shift.get_absolute_url())


class OrganizationMemberNoteUpdateView(OrganizationPermissionMixin, View):
    """Create or update persistent organization-level note for a member."""

    http_method_names = ['post']
    permission_required = 'organizations.override_attendance'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'pk')

    def post(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponse:
        organization = self.get_organization()
        user_pk = kwargs.get('user_pk')
        user = get_object_or_404(BaseUser, pk=user_pk)

        note_obj, _created = OrganizationMemberNote.objects.get_or_create(
            organization=organization,
            user=user,
            defaults={'note': ''}
        )

        form = OrganizationMemberNoteForm(request.POST, instance=note_obj)
        if form.is_valid():
            cleaned_note = form.cleaned_data.get('note', '').strip()
            if not cleaned_note:
                note_obj.delete()
            else:
                form.save()
            messages.success(request, _('Note updated for {user}.').format(user=user.display))
        else:
            messages.error(request, _('Failed to update note: {errors}').format(errors=form.errors))

        success_url = request.POST.get('success_url')
        if success_url:
            return HttpResponseRedirect(str(success_url))
        return HttpResponseRedirect(reverse('organization_attendance_overview', args=[organization.pk]))
