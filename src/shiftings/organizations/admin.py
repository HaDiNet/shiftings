from django.contrib import admin

from shiftings.organizations.models import Membership, MembershipType, Organization, OrganizationDummyUser

admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(MembershipType)
admin.site.register(OrganizationDummyUser)
