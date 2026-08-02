from django.contrib import admin, messages
from django.contrib.auth import get_user_model

from .models import OutgoingEmail
from shiftings.utils.admin import BaseModelAdmin, RelatedObjectsFilter


class SentByUserFilter(RelatedObjectsFilter):
	title = 'sender'
	parameter_name = 'sender'
	related_model = get_user_model()
	related_model_filter = {'sent_emails__isnull': False}
	related_label_field = 'username'
	queryset_filter_field = 'sender'


@admin.register(OutgoingEmail)
class OutgoingEmailAdmin(BaseModelAdmin):
	list_display = ('subject', 'sender', 'from_email', 'recipient_count', 'sent_at')
	search_fields = ('subject', 'body', 'recipients', 'from_email', 'bcc', 'reply_to')
	list_filter = ('sent_at', SentByUserFilter)
	ordering = ('-sent_at',)
	readonly_fields = ('subject', 'body', 'from_email', 'recipients', 'bcc', 'reply_to', 'sent_at', 'sender')

	def has_add_permission(self, request):
		"""Disallow creating new OutgoingEmail objects via the admin UI."""
		return False

	def recipient_count(self, obj: OutgoingEmail) -> int:  # pragma: no cover - admin helper
		if not obj.recipients:
			return 0
		# recipients stored as newline or comma separated
		parts = [p.strip() for p in obj.recipients.replace('\n', ',').split(',') if p.strip()]
		return len(parts)
	recipient_count.short_description = 'Recipient count'
