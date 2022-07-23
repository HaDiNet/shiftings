from datetime import date, datetime
from typing import Any, Optional

import bootstrap_datepicker_plus.widgets as base
from django.forms.renderers import BaseRenderer
from django.utils.translation import get_language


def get_locale() -> str:
    lang = get_language()
    if lang == 'en':
        return 'en-GB'
    return lang or 'en-GB'


def get_date_format_html() -> str:
    if get_language() == 'de':
        return 'DD.MM.YYYY'
    return 'YYYY-MM-DD'


def get_date_format_python() -> str:
    if get_language() == 'de':
        return '%d.%m.%Y'
    return '%Y-%m-%d'


class DatePickerInput(base.DatePickerInput):
    def render(self, name: str, value: Any, attrs: Optional[Any] = None,
               renderer: Optional[BaseRenderer] = None) -> str:
        self.config['options']['locale'] = get_locale()
        self.config['options']['format'] = get_date_format_html()
        date_str = value.strftime(f'{get_date_format_python()}') \
            if value is not None and isinstance(value, date) else value
        return super().render(name, date_str, attrs, renderer)


class DateTimePickerInput(base.DateTimePickerInput):
    def render(self, name: str, value: Any, attrs: Optional[Any] = None,
               renderer: Optional[BaseRenderer] = None) -> str:
        self.config['options']['locale'] = get_locale()
        self.config['options']['format'] = f'{get_date_format_html()} HH:mm'
        date_str = value.strftime(f'{get_date_format_python()} %H:%M') \
            if value is not None and isinstance(value, datetime) else value
        return super().render(name, date_str, attrs, renderer)


class TimePickerInput(base.TimePickerInput):
    def render(self, name: str, value: Any, attrs: Optional[Any] = None,
               renderer: Optional[BaseRenderer] = None) -> str:
        self.config['options']['locale'] = get_locale()
        return super().render(name, value, attrs, renderer)
