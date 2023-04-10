from abc import ABC

from django.db.models import Q
from django.views.generic import TemplateView

from shiftings.shifts.utils.filter_mixin import ShiftFilterMixin
from shiftings.utils.views.base import BaseLoginMixin


class CalendarBaseView(BaseLoginMixin, ShiftFilterMixin, TemplateView, ABC):
    pass