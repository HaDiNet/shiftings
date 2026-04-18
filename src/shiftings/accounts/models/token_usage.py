"""Token usage tracking for one-time-use token enforcement."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TokenUsageLog(models.Model):
    """Track used tokens to prevent replay attacks."""
    
    class TokenType(models.TextChoices):
        EMAIL_CONFIRM = 'email_confirm', _('Email Confirmation')
        PASSWORD_RESET = 'password_reset', _('Password Reset')
    
    user_id = models.IntegerField(help_text=_('User ID (allows tracking even after user deletion)'))
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text=_('SHA256 hash of the token for secure storage')
    )
    token_type = models.CharField(
        max_length=20,
        choices=TokenType.choices,
        help_text=_('Type of token')
    )
    used_at = models.DateTimeField(auto_now_add=True, help_text=_('When token was used'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text=_('IP address that used token'))
    user_agent = models.TextField(null=True, blank=True, help_text=_('User agent that used token'))
    
    class Meta:
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['user_id', 'token_type']),
            models.Index(fields=['used_at']),
        ]
        verbose_name = _('Token Usage Log')
        verbose_name_plural = _('Token Usage Logs')
        default_permissions = ()
    
    def __str__(self):
        return f'{self.get_token_type_display()} - User {self.user_id} at {self.used_at}'


class FailedTokenAttempt(models.Model):
    """Track failed token validation attempts for rate limiting."""
    
    class FailureReason(models.TextChoices):
        INVALID_TOKEN = 'invalid_token', _('Invalid Token')
        EXPIRED_TOKEN = 'expired_token', _('Expired Token')
        INVALID_UID = 'invalid_uid', _('Invalid User ID')
        USER_NOT_FOUND = 'user_not_found', _('User Not Found')
        ALREADY_USED = 'already_used', _('Token Already Used')
        OTHER = 'other', _('Other')
    
    user_id = models.IntegerField(null=True, blank=True, help_text=_('User ID if identifiable'))
    ip_address = models.GenericIPAddressField(help_text=_('IP address of failed attempt'))
    reason = models.CharField(
        max_length=20,
        choices=FailureReason.choices,
        default=FailureReason.OTHER
    )
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['ip_address', 'attempted_at']),
            models.Index(fields=['user_id', 'attempted_at']),
        ]
        verbose_name = _('Failed Token Attempt')
        verbose_name_plural = _('Failed Token Attempts')
        default_permissions = ()
    
    def __str__(self):
        return f'{self.get_reason_display()} - {self.ip_address} at {self.attempted_at}'
