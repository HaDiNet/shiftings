from django.forms import ModelForm

from shiftings.events.models import Event


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['organization', 'name', 'logo', 'email', 'telephone_number', 'website', 'start_date', 'end_date',
                  'description', 'allowed_organizations', 'public']
