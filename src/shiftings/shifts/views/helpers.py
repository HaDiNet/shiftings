"""Helper utilities for shift views."""

from datetime import date, datetime

from shiftings.shifts.models import Shift


def shift_is_past(shift: Shift) -> bool:
    """Check if a shift start time is in the past (before today)."""
    return shift.start.date() < date.today()


def shift_datetime_is_past(shift: Shift) -> bool:
    """Check if a shift start time is in the past (before now)."""
    return shift.start < datetime.now()
