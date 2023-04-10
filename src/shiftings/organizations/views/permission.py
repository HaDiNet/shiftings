from shiftings.organizations.models import Organization
from shiftings.shifts.views.permission import ParticipationPermissionEditView


class OrganizationParticipationPermissionEditView(ParticipationPermissionEditView[Organization]):
    model = Organization
