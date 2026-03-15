from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from shiftings.accounts.models import CalendarToken


class CalendarTokenCreateView(LoginRequiredMixin, View):
    """Create or regenerate a calendar subscription token for the current user."""

    def post(self, request: HttpRequest) -> HttpResponse:
        token, created = CalendarToken.objects.get_or_create(user=request.user)
        if not created:
            token.regenerate()
            messages.success(request, _('Calendar subscription URL regenerated. Old URLs will stop working.'))
        else:
            messages.success(request, _('Calendar subscription URL generated.'))
        return HttpResponseRedirect(reverse('user_profile'))


class CalendarTokenDeleteView(LoginRequiredMixin, View):
    """Revoke the calendar subscription token for the current user."""

    def post(self, request: HttpRequest) -> HttpResponse:
        CalendarToken.objects.filter(user=request.user).delete()
        messages.success(request, _('Calendar subscription URL revoked.'))
        return HttpResponseRedirect(reverse('user_profile'))
