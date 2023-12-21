from datetime import date, timedelta

from django.core.management.base import BaseCommand

from shiftings.shifts.models import RecurringShift


class Command(BaseCommand):
    help = f'Creates recurring shifts within the next days as configured within the shifts.'

    def add_arguments(self, parser):
        parser.add_argument('--shift', type=int, help='create only for the shift with this pk')
        parser.add_argument('--days', type=int, help='override days to create (only works together with --shift)')

    def handle(self, *args, **options):
        if options['shift'] is not None:
            shift = RecurringShift.objects.filter(pk=options['shift']).first()
            if shift is None:
                self.stdout.write(self.style.ERROR(f'Shift with pk {options["shift"]} does not exist.'))
                return
            self.create_shifts_for(shift, options['days'] or shift.auto_create_days)
        for shift in RecurringShift.objects.all():
            self.create_shifts_for(shift, shift.auto_create_days)

    def create_shifts_for(self, shift: RecurringShift, days: int or None = None) -> None:
        for i in range(days):
            day = date.today() + timedelta(days=i)
            if shift.time_frame_type.matches_day(shift, day):
                shift.create_shifts(day)
