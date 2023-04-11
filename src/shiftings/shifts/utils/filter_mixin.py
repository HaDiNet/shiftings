from datetime import datetime

from django.db.models import Q
from django.http import HttpRequest

from shiftings.shifts.forms.filters import ShiftFilterForm


class ShiftFilterMixin:
    request: HttpRequest

    def get_filter_form_kwargs(self):
        kwargs = {arg: self.request.GET.get(arg)
                  for arg in ['own_shifts_checkbox', 'start_after_field', 'end_before_field',
                              'start_after_time_field', 'end_before_time_field']
                  if self.request.GET.get(arg) is not None}
        kwargs.update({arg: self.request.GET.getlist(arg)
                       for arg in ['select_org_field', 'select_event_field']
                       if self.request.GET.get(arg) is not None})
        return kwargs

    def get_form(self):
        kwargs = self.get_filter_form_kwargs()
        if len(kwargs) > 0:
            form = ShiftFilterForm(data=kwargs, user=self.request.user)
        else:
            form = ShiftFilterForm(user=self.request.user)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shift_filter_form'] = self.get_form()
        return context

    def get_filters(self):
        shift_filter = Q()
        form = self.get_form()
        if not form.is_valid():
            return shift_filter
        print(form.cleaned_data)
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
        else:
            if form.cleaned_data['start_after_field'] is not None:
                shift_filter &= Q(start__date__gte=form.cleaned_data['start_after_field'])
            if form.cleaned_data['start_after_time_field'] is not None:
                shift_filter &= Q(start__time__gte=form.cleaned_data['start_after_time_field'])
        if form.cleaned_data['end_before_field'] is not None and form.cleaned_data['end_before_time_field'] is not None:
            shift_filter &= Q(end__lte=datetime.combine(form.cleaned_data['end_before_field'],
                                                        form.cleaned_data['end_before_time_field']))
        else:
            if form.cleaned_data['end_before_field'] is not None:
                shift_filter &= Q(start__date__gte=form.cleaned_data['end_before_field'])
            if form.cleaned_data['end_before_time_field'] is not None:
                shift_filter &= Q(end__time__lte=form.cleaned_data['end_before_time_field'])
        print(shift_filter)
        return shift_filter
