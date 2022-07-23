from typing import Any

from django.conf import settings
from django.contrib.auth.views import (PasswordResetView as DjangoPasswordResetView,
                                       PasswordResetConfirmView as DjangoPasswordResetConfirmView)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class PasswordResetView(DjangoPasswordResetView):
    template_name = 'accounts/password_reset/prompt.html'
    title = _('Password Reset')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data()
        context.update({'ldap_pw_reset_url': settings.LDAP_PASSWORD_RESET_URL})
        return context


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'accounts/password_reset/confirm.html'
    success_url = reverse_lazy('password_reset_success')
    title = _('Confirm Password Reset')
