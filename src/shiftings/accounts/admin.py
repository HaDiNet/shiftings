from django.contrib import admin

from shiftings.accounts.models import CalendarToken, OIDCOfflineToken, User

admin.site.register(User)


@admin.register(CalendarToken)
class CalendarTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created')
    search_fields = ('user__username',)
    readonly_fields = ('created',)


@admin.register(OIDCOfflineToken)
class OIDCOfflineTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated')
    search_fields = ('user__username',)
    readonly_fields = ('updated',)
