from django.urls import reverse
from django.views.generic import DeleteView

from shiftings.organizations.views.organization_base import (
    OrganizationAdminMixin,
    OrganizationCreateUpdateMixin,
    OrganizationObjectRedirectMixin,
)
from shiftings.shifts.forms.type import ShiftTypeForm
from shiftings.shifts.models import ShiftType
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ShiftTypeEditView(OrganizationCreateUpdateMixin, OrganizationAdminMixin, CreateOrUpdateView[ShiftType]):
    model = ShiftType
    form_class = ShiftTypeForm
    set_organization_initial_on_create_only = False

    def test_func(self) -> bool:
        test = super().test_func()
        if self.is_create() or not test:
            return test
        return self.get_object().name != 'System'

    def get_success_url(self):
        return reverse('organization_admin', args=[self.object.organization.pk])


class ShiftTypeDeleteView(OrganizationObjectRedirectMixin, OrganizationAdminMixin, DeleteView):
    model = ShiftType
