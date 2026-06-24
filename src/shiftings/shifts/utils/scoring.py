from __future__ import annotations

from decimal import Decimal
from typing import Iterable, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from shiftings.accounts.models import BaseUser
    from shiftings.shifts.models import Shift


DEFAULT_POINT_WEIGHT = Decimal("1.00")
DEFAULT_IS_MANDATORY = False


class ScoreData(TypedDict):
    attended: int
    excused: int
    missed: int
    score: Decimal


def effective_point_weight(shift: "Shift") -> Decimal:
    """Resolve the points awarded for attending ``shift``.

    Falls back from a per-shift override to the shift type to a global default.
    """
    if shift.point_weight_override is not None:
        return shift.point_weight_override
    if shift.shift_type is not None:
        return shift.shift_type.point_weight
    return DEFAULT_POINT_WEIGHT


def effective_is_mandatory(shift: "Shift") -> bool:
    """Resolve whether ``shift`` is mandatory.

    Falls back from a per-shift override to the shift type to a global default.
    """
    if shift.is_mandatory_override is not None:
        return shift.is_mandatory_override
    if shift.shift_type is not None:
        return shift.shift_type.is_mandatory
    return DEFAULT_IS_MANDATORY


def member_score_data(shifts: Iterable["Shift"], user: "BaseUser",
                      penalty: Decimal) -> ScoreData:
    """Compute attended/excused/missed counts and the score saldo for ``user``.

    The caller is responsible for filtering ``shifts`` to the desired time
    range and to shifts that have already started.
    """
    attended = 0
    excused = 0
    missed = 0
    score = Decimal("0")
    for shift in shifts:
        is_participant = shift.participants.filter(user=user).exists()
        is_excused = shift.excused_users.filter(pk=user.pk).exists()
        if is_participant:
            attended += 1
            score += effective_point_weight(shift)
        elif is_excused:
            excused += 1
        elif effective_is_mandatory(shift):
            missed += 1
            score -= penalty
    return {"attended": attended, "excused": excused, "missed": missed, "score": score}
