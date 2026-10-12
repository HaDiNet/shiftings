from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Optional, TYPE_CHECKING, TypedDict

from shiftings.shifts.models.attendance import AttendanceStatus

if TYPE_CHECKING:
    from shiftings.accounts.models import BaseUser
    from shiftings.organizations.models import Organization
    from shiftings.shifts.models import Shift, ShiftAttendanceOverride


DEFAULT_POINT_WEIGHT = Decimal("1.00")
DEFAULT_IS_MANDATORY = False


class ScoreData(TypedDict):
    attended: int
    excused: int
    missed: int
    score: Decimal
    original_score: Decimal
    points_overridden: bool


class MemberShiftAttendanceRecord(TypedDict):
    shift: Shift
    original_status: AttendanceStatus
    override_status: AttendanceStatus
    effective_status: AttendanceStatus
    original_points: Decimal
    override_points: Optional[Decimal]
    effective_points: Decimal
    is_overridden: bool
    status_overridden: bool
    points_overridden: bool
    shift_note: str
    border_class: str
    inner_class: str
    points_display: str
    status_label: str
    override_id: Optional[int]


class MemberAttendanceRow(TypedDict):
    pk: int
    user: BaseUser
    name: str
    member_note: str
    records: list[MemberShiftAttendanceRecord]
    attended: int
    excused: int
    missed: int
    original_score: Decimal
    effective_score: Decimal
    points_overridden: bool
    score_display: str


def effective_point_weight(shift: Shift) -> Decimal:
    """Resolve the points awarded for attending ``shift``.

    Falls back from a per-shift override to the shift type to a global default.
    """
    if shift.point_weight_override is not None:
        return shift.point_weight_override
    if shift.shift_type is not None:
        return shift.shift_type.point_weight
    return DEFAULT_POINT_WEIGHT


def effective_is_mandatory(shift: Shift) -> bool:
    """Resolve whether ``shift`` is mandatory.

    Falls back from a per-shift override to the shift type to a global default.
    """
    if shift.is_mandatory_override is not None:
        return shift.is_mandatory_override
    if shift.shift_type is not None:
        return shift.shift_type.is_mandatory
    return DEFAULT_IS_MANDATORY


def get_member_shift_attendance(
    shift: Shift,
    user: BaseUser,
    penalty: Decimal,
    override: Optional[ShiftAttendanceOverride] = None,
    is_participant: Optional[bool] = None,
    is_excused: Optional[bool] = None,
) -> MemberShiftAttendanceRecord:
    """Compute detailed original and effective attendance and point data for a user on a shift."""
    if is_participant is None:
        is_participant = shift.participants.filter(user=user).exists()
    if is_excused is None:
        is_excused = shift.excused_users.filter(pk=user.pk).exists()

    if is_participant:
        original_status = AttendanceStatus.PRESENT
        original_points = effective_point_weight(shift)
    elif is_excused:
        original_status = AttendanceStatus.EXCUSED
        original_points = Decimal("0.00")
    elif effective_is_mandatory(shift):
        original_status = AttendanceStatus.UNEXCUSED
        original_points = -penalty
    else:
        original_status = AttendanceStatus.NONE
        original_points = Decimal("0.00")

    override_status = AttendanceStatus.NONE
    override_points: Optional[Decimal] = None
    shift_note = ""
    override_id: Optional[int] = None

    if override is not None:
        override_id = override.pk
        shift_note = override.note or ""
        if override.status != AttendanceStatus.NONE:
            override_status = AttendanceStatus(override.status)
        if override.points_override is not None:
            override_points = override.points_override

    status_overridden = override_status != AttendanceStatus.NONE and override_status != original_status
    effective_status = override_status if override_status != AttendanceStatus.NONE else original_status

    if override_points is not None:
        effective_points = override_points
    elif status_overridden:
        if effective_status == AttendanceStatus.PRESENT:
            effective_points = effective_point_weight(shift)
        elif effective_status == AttendanceStatus.EXCUSED:
            effective_points = Decimal("0.00")
        elif effective_status == AttendanceStatus.UNEXCUSED:
            effective_points = -penalty
        else:
            effective_points = Decimal("0.00")
    else:
        effective_points = original_points

    points_overridden = override_points is not None or (effective_points != original_points)
    is_overridden = status_overridden or points_overridden or bool(shift_note)

    border_map = {
        AttendanceStatus.PRESENT: "border-present",
        AttendanceStatus.EXCUSED: "border-excused",
        AttendanceStatus.UNEXCUSED: "border-unexcused",
        AttendanceStatus.NONE: "border-none",
    }
    inner_map = {
        AttendanceStatus.PRESENT: "inner-present",
        AttendanceStatus.EXCUSED: "inner-excused",
        AttendanceStatus.UNEXCUSED: "inner-unexcused",
        AttendanceStatus.NONE: "inner-none",
    }

    border_class = border_map.get(original_status, "border-none")
    inner_class = inner_map.get(effective_status, "inner-none")

    if points_overridden and original_points != effective_points:
        points_display = f"{original_points:.2f} -> {effective_points:.2f}"
    else:
        points_display = f"{effective_points:.2f}"

    status_label = str(effective_status.label) if hasattr(effective_status, "label") else str(effective_status)

    return {
        "shift": shift,
        "original_status": original_status,
        "override_status": override_status,
        "effective_status": effective_status,
        "original_points": original_points,
        "override_points": override_points,
        "effective_points": effective_points,
        "is_overridden": is_overridden,
        "status_overridden": status_overridden,
        "points_overridden": points_overridden,
        "shift_note": shift_note,
        "border_class": border_class,
        "inner_class": inner_class,
        "points_display": points_display,
        "status_label": status_label,
        "override_id": override_id,
    }


def member_score_data(
    shifts: Iterable[Shift],
    user: BaseUser,
    penalty: Decimal,
    overrides_map: Optional[dict[tuple[int, int], ShiftAttendanceOverride]] = None,
) -> ScoreData:
    """Compute attended/excused/missed counts and points for ``user``, accounting for overrides."""
    attended = 0
    excused = 0
    missed = 0
    score = Decimal("0.00")
    original_score = Decimal("0.00")

    for shift in shifts:
        override = None
        if overrides_map is not None:
            override = overrides_map.get((shift.pk, user.pk))
        elif hasattr(shift, "attendance_overrides"):
            for candidate in shift.attendance_overrides.all():
                if candidate.user_id == user.pk:
                    override = candidate
                    break

        record = get_member_shift_attendance(shift, user, penalty, override=override)
        if record["effective_status"] == AttendanceStatus.PRESENT:
            attended += 1
        elif record["effective_status"] == AttendanceStatus.EXCUSED:
            excused += 1
        elif record["effective_status"] == AttendanceStatus.UNEXCUSED:
            missed += 1

        score += record["effective_points"]
        original_score += record["original_points"]

    points_overridden = score != original_score
    return {
        "attended": attended,
        "excused": excused,
        "missed": missed,
        "score": score,
        "original_score": original_score,
        "points_overridden": points_overridden,
    }


def build_attendance_matrix(
    organization: Organization,
    shifts: list[Shift],
    users: Iterable[BaseUser],
) -> list[MemberAttendanceRow]:
    """Build member attendance matrix rows for all shifts in the time range."""
    from shiftings.organizations.models.note import OrganizationMemberNote
    from shiftings.shifts.models.attendance import ShiftAttendanceOverride

    penalty = getattr(organization.summary_settings, 'no_response_penalty', Decimal('0.33'))

    # Fetch member notes for this organization
    member_notes = {
        note.user.pk: note.note
        for note in OrganizationMemberNote.objects.filter(organization=organization).select_related('user')
    }

    # Fetch overrides for all relevant shifts
    shift_ids = [shift.pk for shift in shifts]
    overrides = ShiftAttendanceOverride.objects.filter(shift_id__in=shift_ids).select_related('shift', 'user')
    overrides_map: dict[tuple[int, int], ShiftAttendanceOverride] = {
        (ov.shift.pk, ov.user.pk): ov for ov in overrides
    }

    # Precompute participant and excused lookups
    shift_participant_pks: dict[int, set[int]] = {
        shift.pk: set(shift.participants.values_list("user_id", flat=True))
        for shift in shifts
    }
    shift_excused_pks: dict[int, set[int]] = {
        shift.pk: set(shift.excused_users.values_list("pk", flat=True))
        for shift in shifts
    }

    rows: list[MemberAttendanceRow] = []
    for user in users:
        records: list[MemberShiftAttendanceRecord] = []
        attended = 0
        excused = 0
        missed = 0
        original_total = Decimal("0.00")
        effective_total = Decimal("0.00")

        for shift in shifts:
            is_part = user.pk in shift_participant_pks.get(shift.pk, set())
            is_exc = user.pk in shift_excused_pks.get(shift.pk, set())
            override = overrides_map.get((shift.pk, user.pk))

            rec = get_member_shift_attendance(
                shift=shift,
                user=user,
                penalty=penalty,
                override=override,
                is_participant=is_part,
                is_excused=is_exc,
            )
            records.append(rec)

            if rec["effective_status"] == AttendanceStatus.PRESENT:
                attended += 1
            elif rec["effective_status"] == AttendanceStatus.EXCUSED:
                excused += 1
            elif rec["effective_status"] == AttendanceStatus.UNEXCUSED:
                missed += 1

            original_total += rec["original_points"]
            effective_total += rec["effective_points"]

        points_overridden = original_total != effective_total
        if points_overridden:
            score_display = f"{original_total:.2f} -> {effective_total:.2f}"
        else:
            score_display = f"{effective_total:.2f}"

        rows.append({
            "pk": user.pk,
            "user": user,
            "name": user.display,
            "member_note": member_notes.get(user.pk, ""),
            "records": records,
            "attended": attended,
            "excused": excused,
            "missed": missed,
            "original_score": original_total,
            "effective_score": effective_total,
            "points_overridden": points_overridden,
            "score_display": score_display,
        })

    rows.sort(key=lambda r: -r["effective_score"])
    return rows
