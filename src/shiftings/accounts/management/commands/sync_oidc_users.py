from __future__ import annotations

import logging

from django.core.management.base import BaseCommand

from shiftings.accounts.models import OIDCOfflineToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync all users with stored OIDC offline tokens (groups, admin status).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--purge-expired',
            action='store_true',
            help='Delete offline tokens that fail to refresh (expired/revoked).',
        )

    def handle(self, *args, **options):
        tokens = OIDCOfflineToken.objects.select_related('user').all()
        total = tokens.count()
        success = 0
        failed = 0

        self.stdout.write(f'Syncing {total} OIDC user(s)...')

        for offline_token in tokens:
            username = offline_token.user.username
            if offline_token.refresh_user_info():
                success += 1
                logger.info('Synced user %s', username)
            else:
                failed += 1
                logger.warning('Failed to sync user %s', username)
                if options['purge_expired']:
                    offline_token.delete()
                    logger.info('Purged expired token for user %s', username)

        self.stdout.write(self.style.SUCCESS(
            f'Done. {success} synced, {failed} failed (of {total} total).'
        ))
