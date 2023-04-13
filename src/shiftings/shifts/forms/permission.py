from typing import Any, Dict, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Model, QuerySet
from django.forms import BaseModelFormSet, ModelChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models import Organization
from shiftings.shifts.models import ParticipationPermission, ParticipationPermissionType


class ParticipationPermissionForm(forms.ModelForm):
    organization = ModelChoiceField(queryset=Organization.objects.all(), empty_label='All Users', required=False)

    class Meta:
        model = ParticipationPermission
        fields = ['organization', 'permission_type_field']

    related_object: Model

    def __init__(self, related_object: Model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_object = related_object
        self.fields['permission_type_field'].choices = ParticipationPermissionType.choices[1:]

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()

        organization = cleaned_data['organization']
        permission = cleaned_data['permission_type_field']

        if organization:
            existing = ParticipationPermission.objects.get_for_instance(self.related_object, None)
            if existing and existing.permission_type >= permission:
                self.add_error('permission_type_field',
                               _('Permission would have no effect. '
                                 'Permission for all Users is more extensive: {perm}')
                               .format(perm=existing.permission_type.label))
                return cleaned_data

        inherited: Optional[QuerySet[ParticipationPermission]] = \
            getattr(self.related_object, 'inherited_participation_permissions', None)
        if inherited:
            existing = inherited.filter(organization=organization).first()
            if existing and existing.permission_type >= permission:
                self.add_error('permission_type_field',
                               _('Permission would have no effect. '
                                 'There is an inherited more extensive permission: {obj} ({perm})')
                               .format(obj=existing.referred_object, perm=existing.permission_type.label))
            elif organization is not None:
                existing = inherited.filter(organization=None).first()
                if existing and existing.permission_type >= permission:
                    self.add_error('permission_type_field',
                                   _('Permission would have no effect. '
                                     'There is an inherited more extensive permission for all Users: {obj} ({perm})')
                                   .format(obj=existing.referred_object, perm=existing.permission_type.label))

        return cleaned_data


class BaseParticipationPermissionFormSet(BaseModelFormSet):
    def clean(self) -> None:
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        organizations = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            organization = form.cleaned_data['organization']
            if organization in organizations:
                if organization is not None:
                    form.add_error('organization',
                                   _('Can only set one permission for organization "{organization}"')
                                   .format(organization=organization))
                form.add_error('organization', _('Can only set one permission for all Users'))
            organizations.append(organization)
        all_users_permissions = [form for form in self.forms if form.cleaned_data['organization'] is None]
        if len(all_users_permissions) > 0:
            all_users_permission = ParticipationPermissionType(
                all_users_permissions[0].cleaned_data['permission_type_field'])
            for form in self.forms:
                if form.cleaned_data['organization'] is not None \
                        and form.cleaned_data['permission_type_field'] <= all_users_permission:
                    form.add_error('permission_type_field',
                                   _('Permission would have no effect. '
                                     'Permission for "All Users" is more extensive: {perm}')
                                   .format(perm=all_users_permission.label))


ParticipationPermissionFormSet = forms.modelformset_factory(ParticipationPermission, ParticipationPermissionForm,
                                                            formset=BaseParticipationPermissionFormSet,
                                                            extra=0, can_delete=True)
