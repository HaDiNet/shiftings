from django.forms import CheckboxSelectMultiple, ModelForm, MultipleChoiceField

from shiftings.shifts.models import OrganizationSummarySettings


class OrganizationShiftSummaryForm(ModelForm):
    default_shift_types = MultipleChoiceField(widget=CheckboxSelectMultiple, choices=[])

    class Meta:
        model = OrganizationSummarySettings
        fields = ['default_time_range_type', 'default_shift_types']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_shift_types'].choices = [type_.choice for type_ in
                                                      self.instance.organization.shift_types.all()]
        if self.instance.default_shift_types is not None:
            default_ids = self.instance.default_shift_types
            self.fields['default_shift_types'].initial = default_ids if len(default_ids) != 0 else \
                self.instance.organization.shift_types.values_list('pk', flat=True)
