from abc import ABC

from django.db.models import Q
from django.views.generic import TemplateView

from shiftings.utils.views.base import BaseLoginMixin


class CalendarBaseView(BaseLoginMixin, TemplateView, ABC):

    def get_filters(self) -> Q:
        shift_filter = Q()
        if 'filter' in self.request.GET:
            if self.request.GET['filter'] == 'own':
                shift_filter &= Q(participants__user=self.request.user)
            elif self.request.GET['filter'] == 'organization' and 'organization' in self.request.GET:
                shift_filter &= Q(organization__pk=self.request.GET.get('organization'))
            elif self.request.GET['filter'] == 'event' and 'event' in self.request.GET:
                shift_filter &= Q(event__pk=self.request.GET.get('event'))
        return shift_filter
