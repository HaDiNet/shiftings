from django.core.management.base import BaseCommand

from shiftings.accounts.models import User

class Command(BaseCommand):
    help = 'Send reminders to users x amount of days before events they are participating in.'

    def handle(self, *args, **options):
        for user in User.objects.filter(reminder__type__ne='', reminder__days_before_event__gte=0):
            user.send_reminders()