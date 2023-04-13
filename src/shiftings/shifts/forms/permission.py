from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet, ModelChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.shifts.models import ParticipationPermission, ParticipationPermissionType


class ParticipationPermissionForm(forms.ModelForm):
    organization = ModelChoiceField(queryset=Organization.objects.all(), empty_label='All Users', required=False)

    class Meta:
        model = ParticipationPermission
        fields = ['organization', 'permission_type_field']

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permission_type_field'].choices = ParticipationPermissionType.choices[1:]


class BaseParticipationPermissionFormSet(BaseModelFormSet):
    def clean(self) -> None:
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        orgs = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            org = form.cleaned_data.get('organization')
            if org in orgs:
                if org is not None:
                    raise ValidationError(_('Can only set one permission for organization "{org}"').format(org=org))
                raise ValidationError(_('Can only set one permission for all Users'))
            orgs.append(org)


ParticipationPermissionFormSet = forms.modelformset_factory(ParticipationPermission, ParticipationPermissionForm,
                                                            formset=BaseParticipationPermissionFormSet,
                                                            extra=0, can_delete=True)
