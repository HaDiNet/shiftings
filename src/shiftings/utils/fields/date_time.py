from __future__ import annotations

from typing import Any

from django import forms
from django.db import models

from shiftings.utils.widgets.date_time import DatePicker, DateTimePicker, TimePicker


class DateField(models.DateField):
    def formfield(self, **kwargs: Any) -> Any:
        kwargs['form_class'] = DateFormField
        return super().formfield(**kwargs)


class DateFormField(forms.DateField):
    widget = DatePicker()


class DateTimeField(models.DateTimeField):
    def formfield(self, **kwargs: Any) -> Any:
        kwargs['form_class'] = DateTimeFormField
        return super().formfield(**kwargs)


class DateTimeFormField(forms.DateTimeField):
    widget = DateTimePicker()


class TimeField(models.TimeField):
    def formfield(self, **kwargs: Any) -> Any:
        kwargs['form_class'] = TimeFormField
        return super().formfield(**kwargs)


class TimeFormField(forms.TimeField):
    widget = TimePicker()
