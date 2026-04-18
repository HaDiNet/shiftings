from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Q

from shiftings.shifts.models import Shift, ShiftType


def get_shifts_for_date(target_date: date) -> Q:
    """Build Q filter for shifts that overlap with the given date.
    
    Matches shifts that:
    - Start on target_date
    - End on target_date (and extends past it)
    - Span across target_date
    """
    return (Q(start__date=target_date) | Q(end__date=target_date, end__gt=target_date) |
            Q(start__lt=target_date, end__gt=target_date))


def build_shift_type_index(shifts: list[Shift]) -> dict[str, Any]:
    add_default = False
    shift_idx_type = {
        'time_containers': {},
        'types': list(ShiftType.objects.filter(shift__in=shifts).distinct())
    }
    for shift in shifts:
        if shift.shift_type is None:
            add_default = True
            type_name = 'Default'
        else:
            type_name = shift.shift_type.name
        shift_idx_type['time_containers'].setdefault(shift.start.hour, {}).setdefault(type_name, []).append(shift)
    if add_default:
        shift_idx_type['types'].append(None)
    return shift_idx_type
