from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.views.generic import DetailView, ListView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.forms.shift import ShiftForm
from shiftings.shifts.models import Shift
from shiftings.utils.views.base import BaseLoginMixin, BaseMixin
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftDetailView(UserPassesTestMixin, BaseLoginMixin, DetailView):
    template_name = 'shifts/shift.html'
    model = Shift
    context_object_name = 'shift'

    def test_func(self) -> bool:
        return self.request.user.has_perm('organizations.admin') or self.get_object().can_see(self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'add_self_form': AddSelfParticipantForm(self.object, initial={
                'user': self.request.user,
            })
        })
        return context


class ShiftEditView(OrganizationPermissionMixin, CreateOrUpdateView):
    model = Shift
    form_class = ShiftForm
    permission_required = 'organizations.edit_shifts'

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, 'org_pk')
        return self.get_object().organization

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        if self.is_create():
            initial['organization'] = self.get_organization()
            initial['start'] = self.request.GET.get('date')
        return initial

    def get_obj(self) -> Optional[Shift]:
        if self.is_create():
            return None
        obj = super().get_object()
        if not isinstance(obj, Shift):
            return None
        return obj

    def get_success_url(self) -> str:
        return reverse('shift', args=[self.object.pk])
