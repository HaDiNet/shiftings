from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from shiftings.events.models import Event


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['organization', 'name', 'logo', 'email', 'telephone_number', 'website', 'start_date', 'end_date',
                  'description', 'allowed_organizations', 'public']

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        start_date = self.cleaned_data['end_date']
        if start_date > end_date:
            raise ValidationError(_('Start date %(start)s was after end_date %(end)s')% {
                'start': start_date,
                'end': end_date
            })
        return end_date
