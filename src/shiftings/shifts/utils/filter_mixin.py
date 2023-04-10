from django.db.models import Q
from django.http import HttpRequest

from shiftings.shifts.forms.filters import ShiftFilterForm


class ShiftFilterMixin:
    request: HttpRequest

    def get_filter_form_initial(self):
        initial = {arg: self.request.GET.get(arg)
                   for arg in ['own_shifts_checkbox', 'start_after_field', 'end_before_field']}
        initial.update({arg: self.request.GET.getlist(arg)
                        for arg in ['select_org_field', 'select_event_field']})
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shift_filter_form'] = ShiftFilterForm(user=self.request.user, initial=self.get_filter_form_initial())
        return context

    def get_filters(self):
        shift_filter = Q()
        if self.request.GET.get('own_shifts_checkbox') == 'on':
            shift_filter &= Q(participants__user=self.request.user)
        if 'select_org_field' in self.request.GET:
            shift_filter &= Q(organization__in=self.request.GET.getlist('select_org_field'))
        if 'select_event_field' in self.request.GET:
            shift_filter &= Q(event__in=self.request.GET.getlist('select_event_field'))
        if 'start_after_field' in self.request.GET and self.request.GET.get('start_after_field') != '':
            shift_filter &= Q(start__gte=self.request.GET.get('start_after_field'))
        if 'end_before_field' in self.request.GET and self.request.GET.get('end_before_field') != '':
            shift_filter &= Q(end__lte=self.request.GET.get('end_before_field'))
        print(shift_filter)
        return shift_filter
