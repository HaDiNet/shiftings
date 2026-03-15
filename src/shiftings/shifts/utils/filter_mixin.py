import functools
from datetime import datetime

from django.db.models import Q
from django.http import HttpRequest

from shiftings.cal.models import CalendarFilter
from shiftings.shifts.forms.filters import ShiftFilterForm


class ShiftFilterMixin:
    request: HttpRequest

    def get_filter_form_kwargs(self):
        kwargs = {arg: self.request.GET.get(arg)
                  for arg in ['own_shifts_checkbox', 'start_after_field', 'end_before_field',
                              'start_after_time_field', 'end_before_time_field', 'hide_public_shifts']
                  if self.request.GET.get(arg) is not None}
        kwargs.update({arg: self.request.GET.getlist(arg)
                       for arg in ['select_org_field', 'select_event_field', 'exclude_public_orgs_field']
                       if self.request.GET.get(arg) is not None})
        return kwargs

    @functools.cached_property
    def _shift_filter_form(self):
        kwargs = self.get_filter_form_kwargs()
        if kwargs:
            form = ShiftFilterForm(data=kwargs, user=self.request.user)
            if form.is_valid():
                self._persist_calendar_filter(form.cleaned_data)
        else:
            saved_kwargs = self._load_calendar_filter_kwargs()
            form = ShiftFilterForm(data=saved_kwargs if saved_kwargs else None, user=self.request.user)
        return form

    def _persist_calendar_filter(self, cleaned_data):
        cal_filter, _ = CalendarFilter.objects.get_or_create(user=self.request.user)
        cal_filter.hide_public_shifts = cleaned_data.get('hide_public_shifts', False)
        cal_filter.save()
        cal_filter.hidden_public_organizations.set(
            cleaned_data.get('exclude_public_orgs_field') or []
        )

    def _load_calendar_filter_kwargs(self):
        try:
            cal_filter = self.request.user.calendar_filter
        except CalendarFilter.DoesNotExist:
            return {}
        kwargs = {}
        if cal_filter.hide_public_shifts:
            kwargs['hide_public_shifts'] = 'on'
        orgs = list(cal_filter.hidden_public_organizations.values_list('id', flat=True))
        if orgs:
            kwargs['exclude_public_orgs_field'] = orgs
        return kwargs

    def get_form(self):
        return self._shift_filter_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shift_filter_form'] = self.get_form()
        return context

    def get_filters(self):
        shift_filter = Q()
        form = self.get_form()
        if not form.is_valid():
            return shift_filter
        if form.cleaned_data['own_shifts_checkbox']:
            shift_filter &= Q(participants__user=self.request.user)
        if form.cleaned_data['select_org_field'].exists():
            shift_filter &= Q(organization__in=form.cleaned_data['select_org_field'])
        if form.cleaned_data['select_event_field'].exists():
            shift_filter &= Q(event__in=form.cleaned_data['select_event_field'])
        if form.cleaned_data['start_after_field'] is not None and \
                form.cleaned_data['start_after_time_field'] is not None:
            shift_filter &= Q(start__gte=datetime.combine(form.cleaned_data['start_after_field'],
                                                          form.cleaned_data['start_after_time_field']))
        elif form.cleaned_data['start_after_field'] is not None:
            shift_filter &= Q(start__date__gte=form.cleaned_data['start_after_field'])
        elif form.cleaned_data['start_after_time_field'] is not None:
            shift_filter &= Q(start__time__gte=form.cleaned_data['start_after_time_field'])
        if form.cleaned_data['end_before_field'] is not None and form.cleaned_data['end_before_time_field'] is not None:
            shift_filter &= Q(end__lte=datetime.combine(form.cleaned_data['end_before_field'],
                                                        form.cleaned_data['end_before_time_field']))
        elif form.cleaned_data['end_before_field'] is not None:
            shift_filter &= Q(end__date__lte=form.cleaned_data['end_before_field'])
        elif form.cleaned_data['end_before_time_field'] is not None:
            shift_filter &= Q(end__time__lte=form.cleaned_data['end_before_time_field'])
        if form.cleaned_data['hide_public_shifts']:
            user_orgs = self.request.user.organizations
            shift_filter &= (
                Q(organization__in=user_orgs) | Q(participants__user=self.request.user)
            )
        elif form.cleaned_data['exclude_public_orgs_field'].exists():
            excluded = form.cleaned_data['exclude_public_orgs_field']
            user_orgs = self.request.user.organizations
            shift_filter &= (
                ~Q(organization__in=excluded) |
                Q(organization__in=user_orgs) |
                Q(participants__user=self.request.user)
            )
        return shift_filter
