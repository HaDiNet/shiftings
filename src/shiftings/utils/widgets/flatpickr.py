from typing import Any, Optional

from django.forms.widgets import DateTimeBaseInput
from django.utils.translation import get_language


class FlatPickrMixin(DateTimeBaseInput):
    template_name = 'flatpickr/flatpickr.html'

    js_format: str
    python_format: str
    no_date: bool
    use_time: bool

    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(attrs, self.python_format)
        self.attrs['class'] = 'flatpickr flatpickr-input'
        self.attrs['js_format'] = self.js_format

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css',
                    'https://npmcdn.com/flatpickr/dist/themes/dark.css')
        }
        js = ('https://cdn.jsdelivr.net/npm/flatpickr', f'js/l10n/{get_language()}.js')

    def get_context(self, name: str, value: Any, attrs: Optional[dict[str, Any]]) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'format': self.js_format,
            'no_date': self.no_date,
            'use_time': self.use_time,
            'locale': get_language()
        })
        return context
