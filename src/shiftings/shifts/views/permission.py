from abc import ABC
from typing import Any, Generic, TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from shiftings.events.models import Event
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization_base import OrganizationPermissionMixin
from shiftings.shifts.forms.permission import ParticipationPermissionFormSet
from shiftings.shifts.models import ParticipationPermission, Shift
from shiftings.utils.views.formset import ModelFormsetBaseView

T = TypeVar('T', bound=Model)


class ParticipationPermissionEditView(OrganizationPermissionMixin, ModelFormsetBaseView[ParticipationPermission],
                                      TemplateView, Generic[T], ABC):
    form_class = ParticipationPermissionFormSet
    template_name = 'shifts/edit_participation_permissions.html'
    permission_required = 'organizations.admin'

    def get_object(self) -> T:
        return super().get_object()

    def get_organization(self) -> Organization:
        obj = self.get_object()
        if isinstance(obj, Organization):
            return obj
        return obj.organization

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['related_object'] = self.get_object()
        return kwargs

    def get_form_queryset(self) -> QuerySet[ParticipationPermission]:
        return self.get_object().participation_permissions.all()

    def get_form_data(self) -> list[ParticipationPermission]:
        return list()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['object'] = obj
        context['organization'] = self.get_organization()
        context['instructions'] = _('<p>Any Permission present will be applied to all Shifts belonging to "{object}". '
                                    'If the object is a shift only this shift will be affected. <br> <br>'
                                    'Permissions can only be more specific than their inherited permissions. '
                                    'You can apply Permissions to "All Users" or specific other organizations.'
                                    '</p>').format(object=obj.display)
        return context

    def form_valid(self, formset: ParticipationPermissionFormSet):
        obj = self.get_object()
        for form in formset.forms:
            form.instance.referred_object_id = obj.pk
            form.instance.referred_content_type = ContentType.objects.get_for_model(obj)
        formset.save()
        return self.success

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()


class ShiftParticipationPermissionEditView(ParticipationPermissionEditView[Shift]):
    model = Shift

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shift = self.get_object()
        context['inherited_permissions'] = shift.inherited_participation_permissions \
            .order_by('referred_content_type', 'referred_object_id')
        return context


class EventParticipationPermissionEditView(ParticipationPermissionEditView[Event]):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['inherited_permissions'] = event.inherited_participation_permissions
        return context
