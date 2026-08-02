from typing import Any

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView

from shiftings.organizations.models import Organization
from shiftings.organizations.models.activity_log import OrganizationActivityLog
from shiftings.organizations.services import log_organization_activity
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.participant import AddOtherParticipantForm, AddSelfParticipantForm
from shiftings.shifts.models import Participant, Shift
from shiftings.shifts.views.helpers import shift_is_past
from shiftings.utils.exceptions import Http403
from shiftings.utils.views.create_update_view import CreateView


def get_participant_name(participant: Participant) -> str:
    return participant.user.display if participant.user else participant.display_name


def log_shift_participant_activity(*,
                                   shift: Shift,
                                   actor,
                                   action: OrganizationActivityLog.Action,
                                   participant: Participant,
                                   summary: str) -> None:
    log_organization_activity(
        organization=shift.organization,
        actor=actor,
        action=action,
        summary=summary.format(participant=get_participant_name(participant)),
        metadata={
            'target_url': shift.get_absolute_url(),
            'target_label': shift.detailed_display,
            'participant_display_name': participant.display_name,
        },
    )


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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        shift = self.get_shift()
        if shift_is_past(shift):
            form = context['form']
            if not hasattr(form, 'cleaned_data'):
                form.cleaned_data = {}
            context['form'].add_error(None, _('This shift is over, do you really want/need to add a participant?'))
        return context

    def form_valid(self, form: AddSelfParticipantForm) -> HttpResponse:
        shift = self.get_shift()
        if (shift_is_past(shift)
                and not self.request.user.has_perm('organizations.add_to_past_shift', self.get_organization())):
            raise Http403("You don't have permission to add participants to past shifts.")
        if (not self.request.user.has_perm('organizations.add_non_members_to_shifts', self.get_organization())
                and not self.get_organization().is_member(form.cleaned_data['user'])):
            raise Http403("You don't have permission to add non-members to this shift.")
        self.save_participant_for_shift(form, shift, OrganizationActivityLog.Action.SHIFT_PARTICIPANT_ADDED_OTHER)
        return self.success

    def save_participant_for_shift(self,
                                   form: AddSelfParticipantForm,
                                   shift: Shift,
                                   action: OrganizationActivityLog.Action) -> None:
        self.object = form.save()
        shift.participants.add(self.object)
        shift.save()

        log_shift_participant_activity(
            shift=shift,
            actor=self.request.user,
            action=action,
            participant=self.object,
            summary=str(_('Shift participant added: {participant}')),
        )

    def get_success_url(self) -> str:
        return self.get_shift().get_absolute_url()


class AddSelfParticipantView(AddOtherParticipantView):
    form_class = AddSelfParticipantForm
    permission_required = 'organizations.participate_in_shift'

    def has_permission(self) -> bool:
        if (shift_is_past(self.get_shift())
                and not self.request.user.has_perm('organizations.add_to_past_shift', self.get_organization())):
            return False
        if self.get_shift().can_participate(self.request.user):
            return True
        return super().has_permission()

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial

    def form_valid(self, form: AddSelfParticipantForm) -> HttpResponse:
        shift = self.get_shift()
        self.save_participant_for_shift(form, shift, OrganizationActivityLog.Action.SHIFT_PARTICIPANT_ADDED_SELF)
        return self.success


class RemoveParticipantView(OrganizationPermissionMixin, DeleteView):
    model = Participant
    pk_url_kwarg = 'ppk'
    permission_required = 'organizations.remove_others_from_shifts'

    def get_organization(self) -> Organization:
        return self.get_shift().organization

    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def has_permission(self) -> bool:
        if shift_is_past(self.get_shift()):
            return self.get_organization().is_admin(self.request.user)
        if self.get_object().user.pk == self.request.user.pk:
            return True
        return super().has_permission()

    def get_success_url(self) -> str:
        if self.request.POST.get('success_url'):
            return str(self.request.POST['success_url'])
        return self.get_shift().get_absolute_url()

    def form_valid(self, form):
        shift = self.get_shift()
        participant = self.object
        response = super().form_valid(form)
        log_shift_participant_activity(
            shift=shift,
            actor=self.request.user,
            action=OrganizationActivityLog.Action.SHIFT_PARTICIPANT_REMOVED,
            participant=participant,
            summary=str(_('Shift participant removed: {participant}')),
        )
        return response
