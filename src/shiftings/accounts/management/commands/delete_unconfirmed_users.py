from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from shiftings.accounts.models import User


class Command(BaseCommand):
    help = f'Delete users, that haven\'t confirmed their emails and whose activation links have expired.'

    def handle(self, *args, **options):
        for user in User.objects.filter(is_active=False):
            if not user.last_login \
                    and user.date_joined + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT) < datetime.now():
                self.stdout.write(f'Deleting user {user.get_full_name()} ({user.username}).')
                user.delete()
