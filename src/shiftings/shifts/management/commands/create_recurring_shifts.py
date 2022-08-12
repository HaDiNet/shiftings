from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from shiftings.shifts.models import RecurringShift


class Command(BaseCommand):
    help = f'Creates recurring shifts within the next {settings.RECURRING_SHIFTS_AUTO_CREATE_DAYS} days.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, help='override days to create')

    def handle(self, *args, **options):
        print(options)
        for i in range(options['days'] or settings.RECURRING_SHIFTS_AUTO_CREATE_DAYS):
            day = date.today() + timedelta(days=i)
            self.stdout.write(self.style.NOTICE(f'Creating for {day}.'))
            for _shift in RecurringShift.objects.all():
                shift: RecurringShift = _shift
                if shift.time_frame_type.matches_day(shift, day):
                    shift.create_shifts(day)
