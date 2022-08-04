from django.contrib import admin

from shiftings.organizations.models import Membership, Organization

admin.site.register(Organization)
admin.site.register(Membership)
