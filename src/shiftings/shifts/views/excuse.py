from typing import Any

from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic.edit import FormView

from shiftings.accounts.models import BaseUser
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.excuse import ExcuseOtherForm
from shiftings.shifts.models import Shift


class _ExcuseShiftMixin(OrganizationPermissionMixin):
    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def get_organization(self) -> Organization:
        return self.get_shift().organization


class ExcuseSelfView(_ExcuseShiftMixin, View):
    """Mark the current user as excused from the shift.

    If the user is already a Participant on this shift, the Participant is
    removed so that changing one's mind from Coming to Excused leaves only
    the excused state.
    """

    http_method_names = ['post']
    permission_required = 'organizations.participate_in_shift'

    def post(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponse:
        shift = self.get_shift()
        for participant in list(shift.participants.filter(user=request.user)):
            shift.participants.remove(participant)
            participant.delete()
        shift.excused_users.add(request.user)
        return HttpResponseRedirect(shift.get_absolute_url())


class ExcuseOtherView(_ExcuseShiftMixin, FormView):
    """Admin form to add another organisation member to the excused list."""

    form_class = ExcuseOtherForm
    template_name = 'generic/form_card.html'
    permission_required = 'organizations.add_members_to_shifts'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['shift'] = self.get_shift()
        return kwargs

    def form_valid(self, form: ExcuseOtherForm) -> HttpResponse:
        shift = self.get_shift()
        user = form.cleaned_data['user']
        for participant in list(shift.participants.filter(user=user)):
            shift.participants.remove(participant)
            participant.delete()
        shift.excused_users.add(user)
        return HttpResponseRedirect(shift.get_absolute_url())

    def get_success_url(self) -> str:
        return self.get_shift().get_absolute_url()


class RemoveExcusedView(_ExcuseShiftMixin, View):
    """Remove a user from the shift's excused list.

    Self may always withdraw (with participate_in_shift); admins with
    remove_others_from_shifts may remove anyone.
    """

    http_method_names = ['post']

    def has_permission(self) -> bool:
        target_pk = int(self.kwargs['user_pk'])
        if target_pk == self.request.user.pk:
            return self.request.user.has_perm(
                'organizations.participate_in_shift', self.get_organization()
            )
        return self.request.user.has_perm(
            'organizations.remove_others_from_shifts', self.get_organization()
        )

    def post(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponse:
        shift = self.get_shift()
        user = BaseUser.objects.filter(pk=kwargs['user_pk']).first()
        if user is not None:
            shift.excused_users.remove(user)
        if request.POST.get('success_url'):
            return HttpResponseRedirect(str(request.POST['success_url']))
        return HttpResponseRedirect(shift.get_absolute_url())
