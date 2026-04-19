from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from shiftings.organizations.models import OrganizationActivityLog


class Command(BaseCommand):
    help = 'Delete organization activity log entries older than 90 days.'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=90)
        deleted_count, _ = OrganizationActivityLog.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f'Deleted {deleted_count} organization activity log entries older than {cutoff}.')
