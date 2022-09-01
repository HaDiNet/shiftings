from django import template

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization
from shiftings.organizations.views.organization import OrganizationAdminView
from shiftings.utils.permissions import has_any_permission

register = template.Library()


@register.simple_tag()
def check_can_see_admin(user: User, organization: Organization):
    return has_any_permission(user, OrganizationAdminView.permission_required, organization)


@register.simple_tag()
def is_organization_admin(user: User, organization: Organization):
    return organization.is_admin(user)
