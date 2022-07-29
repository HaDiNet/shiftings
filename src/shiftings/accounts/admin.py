from django.contrib import admin

from shiftings.accounts.models import Membership, User

admin.site.register(User)
admin.site.register(Membership)
