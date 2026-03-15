from django.contrib import admin

from shiftings.accounts.models import OIDCOfflineToken, User

admin.site.register(User)


@admin.register(OIDCOfflineToken)
class OIDCOfflineTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated')
    search_fields = ('user__username',)
    readonly_fields = ('updated',)
