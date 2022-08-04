from __future__ import annotations

from datetime import date
from typing import Optional

from django.db.models import Q, QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.events.forms.event import EventForm
from shiftings.events.models import Event
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateViewWithImageUpload


class EventListView(BaseMixin, ListView):
    template_name = 'events/list.html'
    model = Event
    context_object_name = 'events'

    def get_queryset(self) -> QuerySet:
        search_param = self.request.GET.get('search_param')
        if search_param is not None:
            return Event.objects.filter(Q(organization__name__icontains=search_param) |
                                        Q(name__icontains=search_param))
        return Event.objects.all()


class FutureEventListView(EventListView):
    extra_context = {
        'future': True
    }
    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return queryset.filter(end_date__gte=date.today())


class EventDetailView(BaseMixin, DetailView):
    template_name = 'events/event.html'
    model = Event
    context_object_name = 'event'


class EventEditView(BaseMixin, CreateOrUpdateViewWithImageUpload):
    model = Event
    form_class = EventForm

    def get_obj(self) -> Optional[Event]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, Event):
            return None
        return obj

    def get_success_url(self) -> str:
        return reverse('event', args=[self.object.pk])
