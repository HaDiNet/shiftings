from django.contrib import admin

from shiftings.organizations.models import Membership, Organization
from shiftings.organizations.models.membership import MembershipType

admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(MembershipType)
