import os
import sys
from pathlib import Path


def setup_db():
    sys.path.append('src')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shiftings.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    (Path('test_db') / 'db.sqlite3').unlink(missing_ok=True)
    execute_from_command_line(['', 'migrate'])
    execute_from_command_line(['', 'loaddata', 'user'])
    execute_from_command_line(['', 'loaddata', 'organization'])
    execute_from_command_line(['', 'loaddata', 'shift'])


if __name__ == '__main__':
    setup_db()
