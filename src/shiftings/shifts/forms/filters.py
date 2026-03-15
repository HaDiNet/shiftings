from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import BooleanField, CheckboxSelectMultiple, ModelMultipleChoiceField, TimeField
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.events.models import Event
from shiftings.organizations.models import Organization
from shiftings.utils.fields.date_time import DateFormField


class ShiftFilterForm(forms.Form):
    own_shifts_checkbox = BooleanField(widget=forms.CheckboxInput, label=_('Shifts I participate in'), required=False)
    select_org_field = ModelMultipleChoiceField(queryset=Organization.objects.none(), widget=CheckboxSelectMultiple,
                                                required=False)
    select_event_field = ModelMultipleChoiceField(queryset=Event.objects.none(), widget=CheckboxSelectMultiple,
                                                  required=False)
    start_after_field = DateFormField(label=_('Date YYYY-MM-DD'), required=False)
    start_after_time_field = TimeField(label=_('Time HH:MM'), required=False)
    end_before_field = DateFormField(label=_('Date YYYY-MM-DD'), required=False)
    end_before_time_field = TimeField(label=_('Time HH:MM'), required=False)
    hide_public_shifts = BooleanField(widget=forms.CheckboxInput, label=_('Hide public shifts'), required=False)
    exclude_public_orgs_field = ModelMultipleChoiceField(queryset=Organization.objects.none(),
                                                         widget=CheckboxSelectMultiple, required=False)

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        orgs = user.organizations
        self.fields['select_org_field'].queryset = orgs
        self.has_orgs = orgs.count() > 0
        events = user.events
        self.fields['select_event_field'].queryset = events
        self.has_events = events.count() > 0

        from shiftings.shifts.models import Shift
        from shiftings.shifts.models.permission import ParticipationPermission, ParticipationPermissionType
        shift_ct = ContentType.objects.get_for_model(Shift)
        public_shift_ids = ParticipationPermission.objects.filter(
            referred_content_type=shift_ct,
            permission_type_field__gte=ParticipationPermissionType.Existence,
            organization__isnull=True
        ).values_list('referred_object_id', flat=True)
        public_orgs = Organization.objects.filter(
            shifts__id__in=public_shift_ids
        ).exclude(id__in=orgs.values('id')).distinct()
        self.fields['exclude_public_orgs_field'].queryset = public_orgs
        self.has_public_orgs = public_orgs.exists()
