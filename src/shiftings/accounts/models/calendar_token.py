from __future__ import annotations

import logging
import secrets
from functools import cache
from typing import Any

import requests
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CalendarToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calendar_token',
        verbose_name=_('User'),
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name=_('Token'),
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return f'{self.user} ({self.token[:8]}...)'

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.token:
            self.token = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def regenerate(self) -> CalendarToken:
        self.token = secrets.token_hex(32)
        self.save(update_fields=['token'])
        return self


@cache
def _get_oidc_endpoints() -> dict[str, str]:
    """Fetch and cache the OpenID Connect discovery document."""
    resp = requests.get(settings.OPENID_CONF_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


class OIDCOfflineToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='oidc_offline_token',
        verbose_name=_('User'),
    )
    refresh_token = models.TextField(verbose_name=_('Refresh Token'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return f'OIDCOfflineToken for {self.user}'

    def refresh_user_info(self) -> bool:
        """Use the stored offline token to refresh the user's OIDC data.

        Returns True on success, False if the token is expired or invalid.
        """
        try:
            endpoints = _get_oidc_endpoints()
            token_endpoint = endpoints['token_endpoint']
            userinfo_endpoint = endpoints['userinfo_endpoint']
        except Exception:
            logger.exception('Failed to fetch OIDC discovery document')
            return False

        client_config = settings.AUTHLIB_OAUTH_CLIENTS['shiftings']

        # Exchange refresh token for new access token
        try:
            token_resp = requests.post(
                token_endpoint,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token,
                    'client_id': client_config['client_id'],
                    'client_secret': client_config['client_secret'],
                },
                timeout=10,
            )
        except Exception:
            logger.exception('Failed to call OIDC token endpoint')
            return False

        if token_resp.status_code != 200:
            logger.warning(
                'OIDC token refresh failed (status %d): %s',
                token_resp.status_code,
                token_resp.text,
            )
            return False

        token_data = token_resp.json()

        # Update stored refresh token
        self.refresh_token = token_data['refresh_token']
        self.save(update_fields=['refresh_token', 'updated'])

        # Fetch current userinfo
        access_token = token_data['access_token']
        try:
            userinfo_resp = requests.get(
                userinfo_endpoint,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10,
            )
        except Exception:
            logger.exception('Failed to call OIDC userinfo endpoint')
            return False

        if userinfo_resp.status_code != 200:
            logger.warning(
                'OIDC userinfo request failed (status %d): %s',
                userinfo_resp.status_code,
                userinfo_resp.text,
            )
            return False

        # Reuse the existing user population logic
        from shiftings.accounts.oidc import populate_user_from_oidc

        populate_user_from_oidc(userinfo_resp.json())
        return True
