# -*- coding: utf-8 -*-
ALLOWED_HOSTS = ['your.domain.example.com']

# Disable Debug Mode
DEBUG = False
TEMPLATE_DEBUG = False

# Production Secret Key
SECRET_KEY = 'your_production_secret_key'

# Enable/disable features at will
FEATURES = {
    'event': False,
    'registration': True,
    'gdpr_template': 'local/gdpr_template.html'
}

# Configure OIDC Options
OAUTH_ENABLED = True
AUTHLIB_OAUTH_CLIENTS = {
    'shiftings': {
        'client_id': 'shiftings',
        'client_secret': 'client_key',
    }
}
OAUTH_ADMIN_GROUP = 'admin_group_name'
OPENID_CONF_URL = 'oidc_url'
OAUTH_USERNAME_CLAIM = 'username'
OAUTH_FIRST_NAME_CLAIM = 'first_name'
OAUTH_LAST_NAME_CLAIM = 'last_name'
OAUTH_GROUP_CLAIM = 'groups'
OAUTH_EMAIL_CLAIM = 'email'
OAUTH_CLIENT_SCOPES = 'scopes'
OAUTH_GROUP_IGNORE_REGEX = r'ignore group regex'

# configure
LDAP_ENABLED = False
# For details see https://django-auth-ldap.readthedocs.io/en/latest/


# Add Database configuration for example postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'shiftings',
        'HOST': 'localhost',
        'USER': 'shiftings_app',
        'PASSWORD': 'db_password',
    }
}

# Configure Email settings
DEFAULT_FROM_EMAIL = 'shiftings@example.com'
EMAIL_SUBJECT_PREFIX = '[Shiftings]'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail-host@example.com'
EMAIL_PORT = 25
SERVER_EMAIL = 'shiftings@example.com'

SITE = 'shiftings.example.com'

# Maximum number of entries for detailed list views
MAX_LIST_ENTRIES = 256

# Token security validation tuning
TOKEN_SECURITY_MAX_FAILED_ATTEMPTS_PER_IP = 5
TOKEN_SECURITY_FAILED_ATTEMPT_WINDOW_HOURS = 1
TOKEN_SECURITY_MAX_FAILED_ATTEMPTS_PER_USER = 10
TOKEN_SECURITY_FAILED_ATTEMPT_WINDOW_USER_HOURS = 24
TOKEN_SECURITY_MAX_TOKEN_LENGTH = 255

MEDIA_URL = '/media/'
# Secure media with login. set the current values are 'apache2' and 'nginx'
SERVE_MEDIA_SERVER = 'apache2'
