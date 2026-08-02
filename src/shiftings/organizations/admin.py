from shiftings.organizations.models import Membership, MembershipType, Organization, OrganizationDummyUser
from shiftings.utils.admin import register_models

register_models(
	Organization,
	Membership,
	MembershipType,
	OrganizationDummyUser,
)
