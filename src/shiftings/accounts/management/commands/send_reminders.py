from django.core.management.base import BaseCommand

from shiftings.accounts.models import User

class Command(BaseCommand):
    help = 'Send reminders to users x amount of days before events they are participating in.'

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.reminders_days_before_event >= 0 and user.reminder_type != '':
                user.send_reminders()
