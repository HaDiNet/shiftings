import logging
from typing import Any

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import (
    INTERNAL_RESET_SESSION_TOKEN,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView, PasswordResetView as DjangoPasswordResetView
)
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.security import TokenSecurityValidator

logger = logging.getLogger(__name__)


class PasswordResetView(DjangoPasswordResetView):
    template_name = 'accounts/password_reset/prompt.html'
    title = _('Password Reset')


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'accounts/password_reset/confirm.html'
    success_url = reverse_lazy('password_reset_success')
    title = _('Confirm Password Reset')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use standard PasswordResetTokenGenerator
        self.token_validator = TokenSecurityValidator(
            PasswordResetTokenGenerator()
        )
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Enhanced password reset with security validation."""
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get the user from decoded uidb64 (Django does this internally)
        user = self.get_user(kwargs.get('uidb64', ''))
        
        if user:
            request_token = kwargs.get('token', '')
            token = request_token
            if request_token == self.reset_url_token:
                token = request.session.get(INTERNAL_RESET_SESSION_TOKEN, '')

            # Check rate limit
            is_allowed, error_msg = self.token_validator.check_rate_limit(
                ip_address=ip_address,
                user_id=user.pk
            )
            if not is_allowed:
                logger.warning(f'Rate limit exceeded for user {user.pk} during password reset from {ip_address}')
                return self.form_invalid(self.get_form())
            
            # Validate token comprehensively
            is_valid, validation_error = self.token_validator.validate_and_check_token(
                user=user,
                token=token,
                token_type='password_reset',
                ip_address=ip_address
            )
            
            if not is_valid:
                logger.warning(f'Password reset token validation failed for user {user.pk}: {validation_error}')
                return self.form_invalid(self.get_form())
            
            # Mark token as used after successful password reset
            response = super().post(request, *args, **kwargs)
            
            # If password was successfully changed, mark token as used
            if response.status_code == 302 and hasattr(response, 'url') and response.url == str(self.success_url):
                self.token_validator.mark_token_used(
                    token=token,
                    user_id=user.pk,
                    token_type='password_reset',
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                logger.info(f'Password reset token marked as used for user {user.pk}')
            
            return response
        
        return super().post(request, *args, **kwargs)
