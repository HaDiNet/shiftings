from django.contrib.auth.tokens import PasswordResetTokenGenerator

from shiftings.accounts.models import User


class EMailConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: User, timestamp: int) -> str:
        return f'{user.pk}{timestamp}{user.is_active}'


email_confirm_token_generator = EMailConfirmTokenGenerator()
