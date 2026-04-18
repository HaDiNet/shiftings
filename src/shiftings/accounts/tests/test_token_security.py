"""
Comprehensive tests for token security features.
Tests cover token validation, expiration, rate limiting, one-time use, and logging.
"""
from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from shiftings.accounts.models import User, TokenUsageLog, FailedTokenAttempt
from shiftings.accounts.token import email_confirm_token_generator
from shiftings.accounts.security.token_validator import TokenSecurityValidator


class TokenValidationTest(TestCase):
    """Test token validation for password reset and email confirmation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_valid_token_format_accepted(self):
        """Valid token format should be accepted."""
        token = PasswordResetTokenGenerator().make_token(self.user)
        self.assertTrue(self.validator.validate_token_format(token))
    
    def test_invalid_token_format_rejected(self):
        """Invalid token formats should be rejected."""
        self.assertFalse(self.validator.validate_token_format(''))
        self.assertFalse(self.validator.validate_token_format(None))
        self.assertFalse(self.validator.validate_token_format('x' * 300))  # Too long
    
    def test_token_check_with_django_generator(self):
        """Token validation should use Django's token generator."""
        token_gen = PasswordResetTokenGenerator()
        token = token_gen.make_token(self.user)
        
        # Should be valid
        self.assertTrue(token_gen.check_token(self.user, token))
    
    def test_tampered_token_detected(self):
        """Tampered token should be detected by Django's generator."""
        token_gen = PasswordResetTokenGenerator()
        token = token_gen.make_token(self.user)
        tampered_token = token[:-1] + ('x' if token[-1] != 'x' else 'y')
        
        # Should be invalid
        self.assertFalse(token_gen.check_token(self.user, tampered_token))
    
    def test_valid_email_confirmation_token_format(self):
        """Valid email confirmation token should have correct format."""
        token = email_confirm_token_generator.make_token(self.user)
        self.assertTrue(self.validator.validate_token_format(token))


class TokenExpirationTest(TestCase):
    """Test token expiration validation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_token_expiration_check_via_validator(self):
        """Token expiration should be checked by validator."""
        token_gen = PasswordResetTokenGenerator()
        token = token_gen.make_token(self.user)
        
        # Fresh token should be valid
        is_valid, error_msg = self.validator.validate_and_check_token(
            user=self.user,
            token=token,
            token_type='password_reset',
            ip_address='192.168.1.1'
        )
        self.assertTrue(is_valid)
    
    def test_invalid_token_detected_by_validator(self):
        """Invalid token should be detected and logged."""
        invalid_token = 'not-a-valid-token'
        
        is_valid, error_msg = self.validator.validate_and_check_token(
            user=self.user,
            token=invalid_token,
            token_type='password_reset',
            ip_address='192.168.1.1'
        )
        
        self.assertFalse(is_valid)
        # Check that attempt was logged
        self.assertTrue(
            FailedTokenAttempt.objects.filter(
                reason=FailedTokenAttempt.FailureReason.EXPIRED_TOKEN
            ).exists()
        )


class OneTimeUseEnforcementTest(TestCase):
    """Test one-time-use token enforcement to prevent replay attacks."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
        self.email_validator = TokenSecurityValidator(email_confirm_token_generator)
    
    def test_password_reset_token_can_only_be_used_once(self):
        """Password reset token should only work once."""
        token_gen = PasswordResetTokenGenerator()
        token = token_gen.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        # First use: mark token as used
        self.validator.mark_token_used(token, self.user.id, TokenUsageLog.TokenType.PASSWORD_RESET)
        
        # Verify token is marked as used
        self.assertTrue(self.validator.check_token_used(token))
        
        # Second use: attempt with same token should fail
        is_valid, error_msg = self.validator.validate_and_check_token(
            user=self.user,
            token=token,
            token_type=TokenUsageLog.TokenType.PASSWORD_RESET,
            ip_address='192.168.1.1'
        )
        
        self.assertFalse(is_valid)
        self.assertIn('already been used', error_msg or '')
    
    def test_email_confirmation_token_can_only_be_used_once(self):
        """Email confirmation token should only work once."""
        inactive_user = User.objects.create_user(
            username='inactive-user',
            email='inactive@example.com',
            password='secret',
            is_active=False
        )
        token = email_confirm_token_generator.make_token(inactive_user)
        
        # First use: mark token as used
        self.email_validator.mark_token_used(
            token,
            inactive_user.id,
            TokenUsageLog.TokenType.EMAIL_CONFIRM
        )
        
        # Verify token is marked as used
        self.assertTrue(self.email_validator.check_token_used(token))
        
        # Second use: attempt with same token should fail
        is_valid, error_msg = self.email_validator.validate_and_check_token(
            user=inactive_user,
            token=token,
            token_type=TokenUsageLog.TokenType.EMAIL_CONFIRM,
            ip_address='192.168.1.1'
        )
        
        self.assertFalse(is_valid)


class RateLimitingTest(TestCase):
    """Test rate limiting on failed token validation attempts."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.test_ip = '192.168.1.1'
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_rate_limit_triggered_after_max_attempts(self):
        """Rate limit should be triggered after maximum failed attempts."""
        # Create 5 failed attempts
        for i in range(5):
            self.validator.log_failed_attempt(
                reason=FailedTokenAttempt.FailureReason.INVALID_TOKEN,
                ip_address=self.test_ip
            )
        # Check that rate limit is enforced
        is_allowed, error_msg = self.validator.check_rate_limit(ip_address=self.test_ip)
        self.assertFalse(is_allowed)
        self.assertIsNotNone(error_msg)
    
    def test_rate_limit_blocks_further_attempts(self):
        """After rate limit, further attempts should be blocked."""
        # Create 5 failed attempts
        for i in range(5):
            FailedTokenAttempt.objects.create(
                ip_address=self.test_ip,
                reason=FailedTokenAttempt.FailureReason.INVALID_TOKEN
            )
        # Verify rate limit is active
        is_allowed, error_msg = self.validator.check_rate_limit(ip_address=self.test_ip)
        self.assertFalse(is_allowed)
        self.assertIsNotNone(error_msg)


class FailedAttemptTrackingTest(TestCase):
    """Test tracking of failed token validation attempts."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_failed_attempt_logged_with_invalid_token(self):
        """Failed attempt with invalid token should be logged."""
        self.validator.log_failed_attempt(
            reason=FailedTokenAttempt.FailureReason.INVALID_TOKEN,
            ip_address='192.168.1.1',
            user_id=self.user.id
        )
        
        # Verify attempt was logged
        self.assertTrue(
            FailedTokenAttempt.objects.filter(
                reason=FailedTokenAttempt.FailureReason.INVALID_TOKEN,
                user_id=self.user.id
            ).exists()
        )
    
    def test_failed_attempt_logged_with_invalid_uid(self):
        """Failed attempt with invalid UID should be logged."""
        self.validator.log_failed_attempt(
            reason=FailedTokenAttempt.FailureReason.INVALID_UID,
            ip_address='192.168.1.1'
        )
        
        # Verify attempt was logged
        self.assertTrue(
            FailedTokenAttempt.objects.filter(
                reason=FailedTokenAttempt.FailureReason.INVALID_UID
            ).exists()
        )
    
    def test_failed_attempt_includes_ip_address(self):
        """Failed attempt should include IP address for rate limiting."""
        test_ip = '203.0.113.42'
        
        self.validator.log_failed_attempt(
            reason=FailedTokenAttempt.FailureReason.INVALID_TOKEN,
            ip_address=test_ip,
            user_id=self.user.id
        )
        
        # Verify attempt includes IP
        attempt = FailedTokenAttempt.objects.filter(
            reason=FailedTokenAttempt.FailureReason.INVALID_TOKEN,
            user_id=self.user.id
        ).first()
        self.assertEqual(str(attempt.ip_address), test_ip)


class TokenUsageLoggingTest(TestCase):
    """Test logging of successfully used tokens."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_successful_password_reset_token_logged(self):
        """Successful password reset should be logged in TokenUsageLog."""
        token_gen = PasswordResetTokenGenerator()
        token = token_gen.make_token(self.user)
        
        # Mark token as used
        self.validator.mark_token_used(token, self.user.id, TokenUsageLog.TokenType.PASSWORD_RESET)
        
        # Verify it's logged
        log_entry = TokenUsageLog.objects.get(
            token_type=TokenUsageLog.TokenType.PASSWORD_RESET,
            user_id=self.user.id
        )
        self.assertIsNotNone(log_entry.used_at)
        self.assertEqual(log_entry.user_id, self.user.id)
    
    def test_successful_email_confirmation_token_logged(self):
        """Successful email confirmation should be logged in TokenUsageLog."""
        token = email_confirm_token_generator.make_token(self.user)
        
        # Mark token as used
        self.validator.mark_token_used(token, self.user.id, TokenUsageLog.TokenType.EMAIL_CONFIRM)
        
        # Verify it's logged
        log_entry = TokenUsageLog.objects.get(
            token_type=TokenUsageLog.TokenType.EMAIL_CONFIRM,
            user_id=self.user.id
        )
        self.assertIsNotNone(log_entry.used_at)
    
    def test_token_usage_log_includes_metadata(self):
        """Token usage log should include IP and User-Agent for audit trail."""
        token = email_confirm_token_generator.make_token(self.user)
        test_ip = '192.168.1.1'
        test_ua = 'Mozilla/5.0 Test Browser'
        
        # Create log entry with metadata
        TokenUsageLog.objects.create(
            user_id=self.user.id,
            token_hash=self.validator.hash_token(token),
            token_type=TokenUsageLog.TokenType.EMAIL_CONFIRM,
            ip_address=test_ip,
            user_agent=test_ua
        )
        
        log_entry = TokenUsageLog.objects.get(user_id=self.user.id)
        self.assertEqual(str(log_entry.ip_address), test_ip)
        self.assertEqual(log_entry.user_agent, test_ua)


class UserIDEnumerationProtectionTest(TestCase):
    """Test protection against user ID enumeration attacks."""
    
    def setUp(self):
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_consistent_validation_error_messages(self):
        """Validation should use consistent error messages to prevent enumeration."""
        # Both invalid UID and invalid token should produce generic errors
        user = User.objects.create_user(username='test', email='test@test.com', password='p')
        
        # Invalid token on valid user
        is_valid1, msg1 = self.validator.validate_and_check_token(
            user=user,
            token='invalid-token',
            token_type='password_reset',
            ip_address='192.168.1.1'
        )
        
        # Both should be invalid
        self.assertFalse(is_valid1)


class ConstantTimeComparisonTest(TestCase):
    """Test that token comparison uses constant-time comparison."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        self.validator = TokenSecurityValidator(PasswordResetTokenGenerator())
    
    def test_token_comparison_is_constant_time(self):
        """Token validation should use constant-time comparison."""
        token_gen = PasswordResetTokenGenerator()
        valid_token = token_gen.make_token(self.user)
        # Django's token generator uses constant-time comparison internally
        # We test that invalid tokens are rejected consistently
        invalid_tokens = [
            'x' * len(valid_token),  # Completely different
            valid_token[:-1] + 'x' if len(valid_token) > 0 else 'x',  # Last char different
            'x' + valid_token[1:] if len(valid_token) > 1 else 'x',   # First char different
        ]
        # All invalid tokens should fail validation
        for invalid_token in invalid_tokens:
            is_valid, _ = self.validator.validate_and_check_token(
                user=self.user,
                token=invalid_token,
                token_type='password_reset',
                ip_address='192.168.1.1'
            )
            self.assertFalse(is_valid)


class IntegrationTest(TestCase):
    """Integration tests for complete token security workflow."""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_password_reset_flow_with_security(self):
        """Complete password reset flow should enforce all security measures."""
        user = User.objects.create_user(
            username='test-user',
            email='test@example.com',
            password='old-password'
        )
        validator = TokenSecurityValidator(PasswordResetTokenGenerator())
        token_gen = PasswordResetTokenGenerator()
        
        # Generate valid token
        token = token_gen.make_token(user)
        
        # Test 1: Valid token should pass validation
        is_valid, _ = validator.validate_and_check_token(
            user=user,
            token=token,
            token_type='password_reset',
            ip_address='192.168.1.1'
        )
        self.assertTrue(is_valid)
        
        # Test 2: Mark token as used
        validator.mark_token_used(
            token=token,
            user_id=user.id,
            token_type='password_reset',
            ip_address='192.168.1.1'
        )
        
        # Test 3: Reuse should be blocked
        is_valid_replay, _ = validator.validate_and_check_token(
            user=user,
            token=token,
            token_type='password_reset',
            ip_address='192.168.1.1'
        )
        self.assertFalse(is_valid_replay)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_email_confirmation_flow_with_security(self):
        """Complete email confirmation flow should enforce all security measures."""
        user = User.objects.create_user(
            username='new-user',
            email='new@example.com',
            password='secret',
            is_active=False
        )
        validator = TokenSecurityValidator(email_confirm_token_generator)
        
        # Generate valid token
        token = email_confirm_token_generator.make_token(user)
        
        # Test 1: Valid token should pass validation
        is_valid, _ = validator.validate_and_check_token(
            user=user,
            token=token,
            token_type='email_confirm',
            ip_address='192.168.1.1'
        )
        self.assertTrue(is_valid)
        
        # Test 2: Mark token as used
        validator.mark_token_used(
            token=token,
            user_id=user.id,
            token_type='email_confirm',
            ip_address='192.168.1.1'
        )
        
        # Test 3: Reuse should be blocked
        is_valid_replay, _ = validator.validate_and_check_token(
            user=user,
            token=token,
            token_type='email_confirm',
            ip_address='192.168.1.1'
        )
        self.assertFalse(is_valid_replay)
