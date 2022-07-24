from django.contrib import admin

from shiftings.accounts.models import Membership, Shifter

admin.site.register(Shifter)
admin.site.register(Membership)
