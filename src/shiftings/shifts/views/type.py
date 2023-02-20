from typing import Any

from django.urls import reverse

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationAdminMixin
from shiftings.shifts.forms.type import ShiftTypeForm
from shiftings.shifts.models import ShiftType
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftTypeEditView(OrganizationAdminMixin, CreateOrUpdateView[ShiftType]):
    model = ShiftType
    form_class = ShiftTypeForm

    def test_func(self) -> bool:
        test = super().test_func()
        if self.is_create() or not test:
            return test
        return self.get_object().name != 'System'

    def get_organization(self) -> Organization:
        if self.is_create():
            return self._get_object(Organization, 'org_pk')
        return self.get_object().organization

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['organization'] = self.get_organization()
        return initial

    def get_success_url(self):
        return reverse('organization_admin', args=[self.object.organization.pk])
