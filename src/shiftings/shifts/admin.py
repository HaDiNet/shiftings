from shiftings.shifts.models import (
    OrganizationSummarySettings, Participant, ParticipationPermission, RecurringShift, Shift, ShiftTemplate,
    ShiftTemplateGroup, ShiftType, ShiftTypeGroup
)
from shiftings.utils.admin import register_models

register_models(
    OrganizationSummarySettings,
    Participant,
    ParticipationPermission,
    RecurringShift,
    Shift,
    ShiftType,
    ShiftTypeGroup,
    ShiftTemplateGroup,
    ShiftTemplate,
)
