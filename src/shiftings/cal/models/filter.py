from django.db import models


class CalendarFilter(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE,
                                related_name='calendar_filter')
    hide_public_shifts = models.BooleanField(default=False)
    hidden_public_organizations = models.ManyToManyField(
        'organizations.Organization', blank=True,
        related_name='hidden_calendar_filters')

    class Meta:
        default_permissions = ()
