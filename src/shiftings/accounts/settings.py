from pathlib import Path

REGISTRATION_FROM_EMAIL = None
REGISTRATION_SUBJECT_PATH = Path(__file__).parent / Path('templates/registration/default_subject.tpl')
REGISTRATION_BODY_PATH = Path(__file__).parent / Path('templates/registration/default_body.tpl')
