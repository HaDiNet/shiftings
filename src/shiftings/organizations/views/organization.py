from __future__ import annotations

from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.organizations.models import Membership
from shiftings.organizations.forms.organization import OrganizationForm
from shiftings.organizations.models import Organization
from shiftings.utils.views.base import BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateViewWithImageUpload


class OrganizationListView(BaseMixin, ListView):
    template_name = 'organizations/list.html'
    model = Organization
    context_object_name = 'organizations'
    extra_context = {
        'full': True
    }

    def get_queryset(self) -> QuerySet[Organization]:
        search_param = self.request.GET.get('search_param')
        if search_param is not None:
            return Organization.objects.filter(name__icontains=search_param)
        return super().get_queryset()


class OwnOrganizationListView(LoginRequiredMixin, ListView):
    template_name = 'organizations/list.html'
    model = Organization
    context_object_name = 'organizations'
    extra_context = {
        'full': False
    }

    def get_queryset(self) -> QuerySet:
        search_param = self.request.GET.get('search_param')
        query = Q(all_members__user=self.request.user)
        if search_param is not None:
            query &= Q(name__icontains=search_param)
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
