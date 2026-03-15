# -*- coding: utf-8 -*-
# Development settings for local Keycloak OIDC login.
# Copy this file to local_settings.py to enable OIDC alongside local auth.
# Requires Keycloak running via: docker compose -f docker-compose.dev.yml up

OAUTH_ENABLED = True
LOCAL_LOGIN_ENABLED = True  # keep both login methods available

AUTHLIB_OAUTH_CLIENTS = {
    'shiftings': {
        'client_id': 'shiftings',
        'client_secret': 'shiftings-dev-secret',
    }
}

OPENID_CONF_URL = 'http://localhost:8080/realms/shiftings/.well-known/openid-configuration'

# Keycloak standard OIDC claim names
OAUTH_USERNAME_CLAIM = 'preferred_username'
OAUTH_FIRST_NAME_CLAIM = 'given_name'
OAUTH_LAST_NAME_CLAIM = 'family_name'
OAUTH_GROUP_CLAIM = 'groups'
OAUTH_EMAIL_CLAIM = 'email'
OAUTH_CLIENT_SCOPES = 'openid profile email'
OAUTH_ADMIN_GROUP = 'admin'
OAUTH_GROUP_IGNORE_REGEX = r'^$'  # don't ignore any groups in dev
