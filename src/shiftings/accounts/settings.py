from pathlib import Path

REGISTRATION_FROM_EMAIL = None
REGISTRATION_SUBJECT_PATH = Path(__file__).parent / Path('templates/registration/default_subject.tpl')
REGISTRATION_BODY_PATH = Path(__file__).parent / Path('templates/registration/default_body.tpl')

# Token security validation settings
TOKEN_SECURITY_MAX_FAILED_ATTEMPTS_PER_IP = 5
TOKEN_SECURITY_FAILED_ATTEMPT_WINDOW_HOURS = 1
TOKEN_SECURITY_MAX_FAILED_ATTEMPTS_PER_USER = 10
TOKEN_SECURITY_FAILED_ATTEMPT_WINDOW_USER_HOURS = 24
TOKEN_SECURITY_MAX_TOKEN_LENGTH = 255
