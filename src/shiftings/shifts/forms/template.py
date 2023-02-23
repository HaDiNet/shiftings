from datetime import timedelta

from django import forms
from django.conf import settings
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

from shiftings.organizations.models import Organization
from shiftings.shifts.models import ShiftTemplate, ShiftTemplateGroup, ShiftType
from shiftings.utils.fields.date_time import DateFormField
from shiftings.utils.fields.integer import TimeSliderField


class SelectOrgShiftTemplateGroupForm(forms.Form):
    template_group = ModelChoiceField(queryset=ShiftTemplateGroup.objects.none())
    date_field = DateFormField(label=_('Date'), help_text=_('Date to create the template on'))

    def __init__(self, organization: Organization, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template_group'].queryset = ShiftTemplateGroup.objects.filter(
            organization=organization).order_by('place', 'name')


class ShiftTemplateGroupForm(forms.ModelForm):
    class Meta:
        model = ShiftTemplateGroup
        fields = ['organization', 'name', 'place', 'start_time']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['organization'].disabled = True


class ShiftTemplateForm(forms.ModelForm):
    start_delay = TimeSliderField(min_value=0, initial=0, max_value=settings.MAX_SHIFT_LENGTH_MINUTES,
                                  step=settings.SHIFT_SLIDER_STEP, label=_('Start Delay'), required=False)
    duration = TimeSliderField(min_value=0, initial=0, max_value=settings.MAX_SHIFT_LENGTH_MINUTES,
                               step=settings.SHIFT_SLIDER_STEP, label=_('Duration'), required=False)

    template_group: ShiftTemplateGroup

    class Meta:
        model = ShiftTemplate
        fields = ['name', 'shift_type', 'start_delay', 'duration', 'required_users', 'max_users', 'additional_infos']

    def __init__(self, template_group: ShiftTemplateGroup, **kwargs):
        self.template_group = template_group
        print(self.base_fields)
        self.declared_fields['start_delay'].set_start(template_group.start_time.strftime('%H:%M'))
        self.declared_fields['duration'].set_start(template_group.start_time.strftime('%H:%M'))
        self.base_fields['shift_type'].queryset = ShiftType.objects.organization(template_group.organization)
        super().__init__(**kwargs)

    def clean_start_delay(self) -> timedelta:
        minutes = self.cleaned_data['start_delay']
        return timedelta(minutes=minutes)

    def clean_duration(self) -> timedelta:
        minutes = self.cleaned_data['duration']
        return timedelta(minutes=minutes)


ShiftTemplateFormSet = forms.modelformset_factory(ShiftTemplate, ShiftTemplateForm, extra=0, can_delete=True)
