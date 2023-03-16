from typing import Any

from django.conf import settings
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjangoPasswordResetConfirmView, PasswordResetView as DjangoPasswordResetView
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class PasswordResetView(DjangoPasswordResetView):
    template_name = 'accounts/password_reset/prompt.html'
    title = _('Password Reset')


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'accounts/password_reset/confirm.html'
    success_url = reverse_lazy('password_reset_success')
    title = _('Confirm Password Reset')
