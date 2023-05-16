from typing import Any, Optional

from django.db.models import QuerySet

from shiftings.accounts.models import User
from shiftings.mail.forms.mail import OrganizationMailForm, ShiftParticipantMailForm
from shiftings.mail.views.mail import BaseMailView
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.models import Shift


class ShiftParticipantsMailView(OrganizationPermissionMixin, BaseMailView):
    form_class = ShiftParticipantMailForm
    permission_required = 'organization.send_mail'
    pk_url_kwarg = 'org_pk'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs

    def get_replacements(self) -> dict[str, str]:
        replacements = super().get_replacements()
        organization = self.get_organization()
        replacements['name'] = organization.name
        return replacements

    def get_organization(self) -> Organization:
        return self._get_object(Organization, self.pk_url_kwarg)

    def get_users(self, form: Optional[ShiftParticipantMailForm] = None) -> QuerySet[User]:
        if form is None:
            return User.objects.none()
        shifts = Shift.objects.filter(start__gte=form.cleaned_data['start'], end__lte=form.cleaned_data['end'])
        if form.cleaned_data['shift_types']:
            shifts = shifts.filter(shift_type__in=form.cleaned_data['shift_types'])
        participant_pks = shifts.values_list('participants__user__pk', flat=True)
        return User.objects.filter(pk__in=participant_pks).distinct()

    def get_success_url(self) -> str:
        return self.get_organization().get_absolute_url()
