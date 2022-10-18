from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.events.forms.event import EventForm
from shiftings.events.models import Event
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.utils.typing import UserRequest
from shiftings.utils.views.base import BaseMixin, BasePermissionMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateViewWithImageUpload


class EventListView(BasePermissionMixin, ListView):
    template_name = 'events/list.html'
    model = Event
    context_object_name = 'events'
    permission_required = 'organizations.admin'

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
        return super().get_queryset().filter(end_date__gte=date.today())


class MyEventsListView(BaseMixin, ListView):
    template_name = 'events/list.html'
    model = Event
    context_object_name = 'events'

    request: UserRequest

    def get_queryset(self) -> QuerySet:
        search_param = self.request.GET.get('search_param')
        query = Q()
        if search_param is not None:
            query &= (Q(organization__name__icontains=search_param) | Q(name__icontains=search_param))
        if self.request.user.is_authenticated:
            return self.request.user.events.filter(query)
        return Event.objects.filter(public=True).filter(query)


class MyFutureEventListView(MyEventsListView):
    extra_context = {
        'future': True
    }

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(end_date__gte=date.today())


class EventMixin(UserPassesTestMixin, BaseMixin, ABC):
    request: UserRequest

    def get_event(self) -> Event:
        return self._get_object(Event, 'pk')

    def test_func(self) -> bool:
        if not self.request.user.is_authenticated:
            return self.get_event().public
        return self.get_event().can_see(self.request.user)


class EventDetailView(EventMixin, DetailView):
    template_name = 'events/event.html'
    model = Event
    context_object_name = 'event'


class EventEditView(BasePermissionMixin, CreateOrUpdateViewWithImageUpload):
    model = Event
    form_class = EventForm
    permission_required = 'organizations.edit_events'

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['organization'] = self.get_organization()
        return initial

    def get_event(self) -> Event:
        return self._get_object(Event, 'pk')

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, 'org_pk')
        return self.get_event().organization

    def get_obj(self) -> Optional[Event]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, Event):
            return None
        return obj

    def has_permission(self) -> bool:
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.has_perm(self.permission_required, self.get_organization())

    def get_success_url(self) -> str:
        return reverse('event', args=[self.object.pk])
