from django.contrib import admin

from shiftings.shifts.models import RecurringShift, Shift, ShiftType

admin.site.register(RecurringShift)
admin.site.register(Shift)
admin.site.register(ShiftType)
