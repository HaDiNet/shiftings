from __future__ import annotations

from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.organizations.forms.organization import OrganizationForm
from shiftings.organizations.models import Organization
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateViewWithImageUpload


class OrganizationListView(BaseMixin, ListView):
    template_name = 'organizations/list.html'
    model = Organization
    context_object_name = 'organizations'


class OwnOrganizationListView(LoginRequiredMixin, ListView):
    template_name = 'organizations/list.html'
    model = Organization
    context_object_name = 'organizations'

    def get_queryset(self) -> QuerySet:
        query = Q(managers__user=self.request.user) \
                | Q(members__user=self.request.user) \
                | Q(helpers__user=self.request.user)
        return Organization.objects.filter(query)


class OrganizationDetailView(BaseMixin, DetailView):
    template_name = 'organizations/organization.html'
    model = Organization
    context_object_name = 'organization'


class OrganizationEditView(BaseMixin, CreateOrUpdateViewWithImageUpload):
    model = Organization
    form_class = OrganizationForm

    def get_obj(self) -> Optional[Organization]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, Organization):
            return None
        return obj

    def get_success_url(self) -> str:
        return reverse('organization', args=[self.object.pk])
