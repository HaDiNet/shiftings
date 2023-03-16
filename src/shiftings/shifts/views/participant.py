from typing import Any

from django.http import HttpResponse
from django.views.generic import DeleteView

from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.participant import AddOtherParticipantForm, AddSelfParticipantForm
from shiftings.shifts.models import Participant, Shift
from shiftings.utils.exceptions import Http403
from shiftings.utils.views.create_update_view import CreateView


class AddOtherParticipantView(OrganizationPermissionMixin, CreateView):
    model = Participant
    form_class = AddOtherParticipantForm
    permission_required = ('organizations.add_non_members_to_shifts', 'organizations.add_members_to_shifts')
    require_only_one = True

    object: Participant

    def get_organization(self) -> Organization:
        return self.get_shift().organization

    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['shift'] = self.get_shift()
        return kwargs

    def form_valid(self, form: AddSelfParticipantForm) -> HttpResponse:
        if not self.request.user.has_perm('organizations.add_non_members_to_shifts', self.get_organization()):
            if not self.get_organization().is_member(form.cleaned_data['user']):
                raise Http403()
        self.object = form.save()
        shift = self.get_shift()
        shift.participants.add(self.object)
        shift.save()
        return self.success

    def get_success_url(self) -> str:
        return self.get_shift().get_absolute_url()


class AddSelfParticipantView(AddOtherParticipantView):
    form_class = AddSelfParticipantForm
    permission_required = 'organizations.participate_in_shift'

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial


class RemoveParticipantView(OrganizationPermissionMixin, DeleteView):
    model = Participant
    pk_url_kwarg = 'ppk'
    permission_required = 'organizations.remove_others_from_shifts'

    def get_organization(self) -> Organization:
        return self.get_shift().organization

    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def has_permission(self) -> bool:
        if self.get_object().user == self.request.user:
            return True
        return super().has_permission()

    def get_success_url(self) -> str:
        if self.request.POST.get('success_url'):
            return str(self.request.POST['success_url'])
        return self.get_shift().get_absolute_url()
