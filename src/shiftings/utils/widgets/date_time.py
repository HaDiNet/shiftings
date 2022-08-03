from django.forms import DateInput, DateTimeInput, TimeInput
from django.utils.translation import get_language

from shiftings.utils.widgets.flatpickr import FlatPickrMixin


def get_locale() -> str:
    lang = get_language()
    if lang == 'en':
        return 'en-GB'
    return lang or 'en-GB'


def get_date_format_html() -> str:
    if get_language() == 'de':
        return 'd.m.Y'
    return 'Y-m-d'


def get_time_format_html() -> str:
    return 'H:i'


def get_date_format_python() -> str:
    if get_language() == 'de':
        return '%d.%m.%Y'
    return '%Y-%m-%d'


def get_time_format_python() -> str:
    return '%H:%M'


class DatePicker(FlatPickrMixin, DateInput):
    js_format = get_date_format_html()
    python_format = get_date_format_python()
    no_date = False
    use_time = False


class DateTimePicker(FlatPickrMixin, DateTimeInput):
    js_format = f'{get_date_format_html()} {get_time_format_html()}'
    python_format = f'{get_date_format_python()} {get_time_format_python()}'
    no_date = False
    use_time = True


class TimePicker(FlatPickrMixin, TimeInput):
    js_format = get_time_format_html()
    python_format = get_time_format_python()
    no_date = True
    use_time = True
