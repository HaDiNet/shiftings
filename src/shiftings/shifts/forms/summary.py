from django.forms import CheckboxSelectMultiple, ModelForm, MultipleChoiceField

from shiftings.shifts.models import OrganizationSummarySettings


class OrganizationShiftSummaryForm(ModelForm):
    class Meta:
        model = OrganizationSummarySettings
        fields = ['default_time_range_type', 'other_shifts_group_name']
