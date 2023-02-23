from datetime import timedelta
from typing import Any, Union

from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import IntegerField

from shiftings.utils.widgets.slider import TimeSliderWidget

MIN_INT: int = -2147483648
MAX_INT: int = 2147483647


class EnhancedIntegerField(IntegerField):
    def __init__(self, *, max_value: int = None, min_value: int = None, **kwargs: Any) -> None:
        if min_value is None or min_value < MIN_INT:
            min_value = MIN_INT
        if max_value is None or max_value > MAX_INT:
            max_value = MAX_INT
        super().__init__(max_value=max_value, min_value=min_value, **kwargs)

    def set_min_value(self, min_value: int) -> None:
        self.min_value = min_value
        self.validators.append(MinValueValidator(min_value))
        self.widget.attrs['min'] = min_value

    def set_max_value(self, max_value: int) -> None:
        self.max_value = max_value
        self.validators.append(MaxValueValidator(max_value))
        self.widget.attrs['max'] = max_value


class TimeSliderField(EnhancedIntegerField):
    widget = TimeSliderWidget
    step: int
    start: str

    def __init__(self, *, step: int = 1, start: str = '0:00', **kwargs: Any) -> None:
        self.step = step
        self.start = start
        super().__init__(**kwargs)

    def set_step(self, step: int) -> None:
        self.step = step
        self.widget.attrs['step'] = step

    def set_start(self, start: str) -> None:
        self.start = start
        self.widget.attrs['start'] = start

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['step'] = self.step
        attrs['start'] = self.start
        return attrs

    def prepare_value(self, value: Union[int, timedelta]) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, timedelta):
            return value.total_seconds() // 60
        return int(value)
