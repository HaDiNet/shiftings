from datetime import timedelta

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from shiftings.shifts.models import ShiftTemplate, ShiftTemplateGroup
from shiftings.utils.fields.integer import TimeSliderField


class ShiftTemplateGroupForm(forms.ModelForm):
    class Meta:
        model = ShiftTemplateGroup
        fields = ['organization', 'name', 'place', 'start_time']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['organization'].disabled = True


class ShiftTemplateForm(forms.ModelForm):
    start_delay = TimeSliderField(min_value=0, initial=0, max_value=settings.MAX_SHIFT_LENGTH_MINUTES,
                                  step=settings.SHIFT_SLIDER_STEP, label=_('Content Amount'), required=False)
    duration = TimeSliderField(min_value=0, initial=0, max_value=settings.MAX_SHIFT_LENGTH_MINUTES,
                               step=settings.SHIFT_SLIDER_STEP, label=_('Content Amount'), required=False)

    template_group: ShiftTemplateGroup

    class Meta:
        model = ShiftTemplate
        fields = ['name', 'shift_type', 'start_delay', 'duration', 'required_users', 'max_users', 'additional_infos']

    def __init__(self, template_group: ShiftTemplateGroup, **kwargs):
        self.template_group = template_group
        self.declared_fields['start_delay'].set_start(template_group.start_time.strftime('%H:%M'))
        self.declared_fields['duration'].set_start(template_group.start_time.strftime('%H:%M'))
        super().__init__(**kwargs)

    def clean_start_delay(self) -> timedelta:
        minutes = self.cleaned_data['start_delay']
        return timedelta(minutes=minutes)

    def clean_duration(self) -> timedelta:
        minutes = self.cleaned_data['duration']
        return timedelta(minutes=minutes)


ShiftTemplateFormSet = forms.modelformset_factory(ShiftTemplate, ShiftTemplateForm, extra=0, can_delete=True)
