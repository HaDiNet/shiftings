from __future__ import annotations

from django.conf import settings
from django.db import models


class OutgoingEmail(models.Model):
    """A simple log model for outgoing emails sent via the application.

    Stores basic metadata and full body so admins can inspect and export messages.
    """

    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField()
    recipients = models.TextField(help_text='Comma- or newline-separated recipient addresses')
    bcc = models.TextField(blank=True, null=True)
    reply_to = models.EmailField(blank=True, null=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sent_emails')
    sent_at = models.DateTimeField(auto_now_add=True)
    attachments = models.TextField(blank=True, null=True, help_text='JSON or comma-separated attachment metadata')

    class Meta:
        ordering = ('-sent_at',)
        verbose_name = 'Outgoing email'
        verbose_name_plural = 'Outgoing emails'

    def __str__(self) -> str:  # pragma: no cover - trivial
        when = self.sent_at.strftime('%Y-%m-%d %H:%M') if self.sent_at else 'unsent'
        return f"{self.subject} — {when}"

    def recipients_list(self) -> list[str]:
        if not self.recipients:
            return []
        parts = [p.strip() for p in self.recipients.replace('\n', ',').split(',') if p.strip()]
        return parts
