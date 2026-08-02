"""Token security utilities for validation and rate limiting."""
import hashlib
import logging
from datetime import timedelta
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import FailedTokenAttempt, TokenUsageLog

logger = logging.getLogger(__name__)


class TokenSecurityValidator:
    """Validate tokens with security checks including expiration and replay protection."""
    
    def __init__(self, token_generator: PasswordResetTokenGenerator):
        self.token_generator = token_generator
        self.max_failed_attempts_per_ip = getattr(settings, 'TOKEN_SECURITY_MAX_FAILED_ATTEMPTS_PER_IP', 5)
        self.failed_attempt_window_hours = getattr(settings, 'TOKEN_SECURITY_FAILED_ATTEMPT_WINDOW_HOURS', 1)
        self.max_failed_attempts_per_user = getattr(settings, 'TOKEN_SECURITY_MAX_FAILED_ATTEMPTS_PER_USER', 10)
        self.failed_attempt_window_user_hours = getattr(settings, 'TOKEN_SECURITY_FAILED_ATTEMPT_WINDOW_USER_HOURS', 24)
        self.max_token_length = getattr(settings, 'TOKEN_SECURITY_MAX_TOKEN_LENGTH', 255)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token for secure storage."""
        return hashlib.sha256(force_bytes(token)).hexdigest()
    
    def check_token_used(self, token: str) -> bool:
        """Check if token has already been used."""
        token_hash = self.hash_token(token)
        return TokenUsageLog.objects.filter(token_hash=token_hash).exists()
    
    def mark_token_used(self, token: str, user_id: int, token_type: str,
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        """Mark token as used to prevent replay attacks."""
        token_hash = self.hash_token(token)
        TokenUsageLog.objects.create(
            user_id=user_id,
            token_hash=token_hash,
            token_type=token_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        logger.info(
            f'Token marked as used: user_id={user_id}, type={token_type}, ip={ip_address}'
        )
    
    def check_rate_limit(self, ip_address: Optional[str] = None, user_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Check if rate limits are exceeded.
        
        Returns:
            (is_allowed, error_message) tuple
        """
        if ip_address:
            # Check IP-based rate limit
            window_start = timezone.now() - timedelta(hours=self.failed_attempt_window_hours)
            ip_attempts = FailedTokenAttempt.objects.filter(
                ip_address=ip_address,
                attempted_at__gte=window_start
            ).count()
            
            if ip_attempts >= self.max_failed_attempts_per_ip:
                logger.warning(
                    f'Rate limit exceeded for IP {ip_address}: '
                    f'{ip_attempts} failed attempts in last {self.failed_attempt_window_hours} hour(s)'
                )
                return False, _('Too many failed attempts. Please try again later.')
        
        if user_id:
            # Check user-based rate limit
            window_start = timezone.now() - timedelta(hours=self.failed_attempt_window_user_hours)
            user_attempts = FailedTokenAttempt.objects.filter(
                user_id=user_id,
                attempted_at__gte=window_start
            ).count()
            
            if user_attempts >= self.max_failed_attempts_per_user:
                logger.warning(
                    f'Rate limit exceeded for user {user_id}: '
                    f'{user_attempts} failed attempts in last {self.failed_attempt_window_user_hours} hour(s)'
                )
                return False, _('Too many failed attempts. Please contact support.')
        
        return True, None
    
    def log_failed_attempt(self, reason: str, ip_address: Optional[str] = None,
                          user_id: Optional[int] = None) -> None:
        """Log failed token attempt for rate limiting and security monitoring."""
        FailedTokenAttempt.objects.create(
            user_id=user_id,
            ip_address=ip_address,
            reason=reason
        )
        logger.warning(
            f'Failed token validation: reason={reason}, user_id={user_id}, ip={ip_address}'
        )
    
    def validate_token_format(self, token: str) -> bool:
        """Validate token format (basic length and character checks)."""
        if not token or not isinstance(token, str):
            return False
        # Django tokens are typically 1-40 characters
        if len(token) < 1 or len(token) > self.max_token_length:
            return False
        return True
    
    def validate_and_check_token(self, user, token: str, token_type: str,
                                ip_address: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Comprehensive token validation.
        
        Returns:
            (is_valid, error_message) tuple
        """
        # Check rate limit first
        is_allowed, error_msg = self.check_rate_limit(ip_address=ip_address, user_id=user.pk if user else None)
        if not is_allowed:
            self.log_failed_attempt(
                FailedTokenAttempt.FailureReason.OTHER,
                ip_address=ip_address,
                user_id=user.pk if user else None
            )
            return False, error_msg
        
        # Validate token format
        if not self.validate_token_format(token):
            self.log_failed_attempt(
                FailedTokenAttempt.FailureReason.INVALID_TOKEN,
                ip_address=ip_address,
                user_id=user.pk if user else None
            )
            logger.error(f'Invalid token format for user {user.pk if user else "unknown"}')
            return False, _('Invalid token format.')
        
        # Check if token has already been used
        if self.check_token_used(token):
            self.log_failed_attempt(
                FailedTokenAttempt.FailureReason.ALREADY_USED,
                ip_address=ip_address,
                user_id=user.pk if user else None
            )
            logger.warning(f'Token replay attempt for user {user.pk if user else "unknown"} from IP {ip_address}')
            return False, _('This link has already been used.')
        
        # Check token validity with Django's token generator
        if not self.token_generator.check_token(user, token):
            # Check if it's an expired token
            # Django's token generator considers tokens valid for PASSWORD_RESET_TIMEOUT (default 3 days)
            self.log_failed_attempt(
                FailedTokenAttempt.FailureReason.EXPIRED_TOKEN,
                ip_address=ip_address,
                user_id=user.pk
            )
            logger.warning(f'Token validation failed (likely expired) for user {user.pk} from IP {ip_address}')
            return False, _('This link has expired. Please request a new one.')
        
        return True, None
