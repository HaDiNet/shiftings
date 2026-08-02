from django.contrib import admin

from shiftings.accounts.models import User
from shiftings.utils.admin import BaseModelAdmin


@admin.register(User)
class UserAdmin(BaseModelAdmin):
	search_fields = (
		'username',
		'first_name',
		'last_name',
		'display_name',
		'email',
	)
	list_filter = (
		'is_active',
		'is_staff',
		'is_superuser',
	)
	actions = BaseModelAdmin.actions + ('toggle_active','send_email_to_selected',)
