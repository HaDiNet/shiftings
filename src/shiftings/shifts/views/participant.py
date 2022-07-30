from typing import Any

from django.http import HttpResponse
from django.views.generic import DeleteView

from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.models import Participant, Shift
from shiftings.utils.views.base import BaseLoginMixin
from shiftings.utils.views.create_update_view import CreateView


class AddSelfParticipantView(BaseLoginMixin, CreateView):
    model = Participant
    form_class = AddSelfParticipantForm

    object: Participant

    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['shift'] = self.get_shift()
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial

    def form_valid(self, form: AddSelfParticipantForm) -> HttpResponse:
        self.object = form.save()
        shift = self.get_shift()
        shift.participants.add(self.object)
        shift.save()
        return self.success


class RemoveParticipantView(BaseLoginMixin, DeleteView):
    model = Participant
    pk_url_kwarg = 'ppk'

    def get_shift(self) -> Shift:
        return self._get_object(Shift, 'pk')

    def get_success_url(self) -> str:
        return self.get_shift().get_absolute_url()
