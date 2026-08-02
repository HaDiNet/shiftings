"""Helper functions for calendar feed views."""

from typing import Any

from django.http import HttpRequest

from shiftings.accounts.models.user import User
from shiftings.organizations.models.organization import Organization
from shiftings.utils.exceptions import Http403

class FeedAccessMixin:
    """Access policy helpers shared by feed views."""

    def ensure_authenticated(self, request: HttpRequest) -> None:
        """Raise Http403 if user is not authenticated."""
        if not request.user.is_authenticated:
            raise Http403()

    def ensure_org_member_or_admin(self, organization: Organization, user: User) -> None:
        """Raise Http403 if user is neither org member nor admin."""
        if not organization.is_member(user) and not organization.is_admin(user):
            raise Http403()
