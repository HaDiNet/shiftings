from datetime import date
from typing import Any, Dict

from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView

from shiftings.accounts.forms.user_form import UserCreateForm, UserUpdateForm
from shiftings.accounts.models import User
from shiftings.accounts.token import email_confirm_token_generator
from shiftings.shifts.models import Shift
from shiftings.shifts.utils.filter_mixin import ShiftFilterMixin
from shiftings.utils.pagination import get_pagination_context
from shiftings.utils.views.base import BaseLoginMixin


class UserProfileView(BaseLoginMixin, ShiftFilterMixin, DetailView):
    model = User
    object: User
    save_path_in_session = True
    title = _('My Shifts')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = date.today()
        if self.request.path == reverse('user_profile_past'):
            shifts = Shift.objects.filter(start__date__lt=today, participants__user=self.object)
        else:
            shifts = Shift.objects.filter(Q(start__date__gte=today) &
                                          (Q(event__in=self.object.events) |
                                           Q(organization__in=self.object.organizations) |
                                           Q(participants__user=self.object)))
        context['shifts'] = get_pagination_context(self.request, shifts.filter(self.get_filters()), 5, 'shifts')
        return context


@method_decorator(sensitive_post_parameters('password', 'confirm_password'), name='dispatch')
class UserRegisterView(CreateView):
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy('user_profile')
    extra_context = {
        'create': True
    }

    def form_valid(self, form: UserCreateForm) -> HttpResponse:
        user = form.instance
        user.password = make_password(form.cleaned_data.get('password'))
        user.is_active = False
        response = super().form_valid(form)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_confirm_token_generator.make_token(user)
        url = reverse('confirm_email', args=[uidb64, token])
        confirm_url = f'{self.request.scheme}://{get_current_site(self.request)}{url}'
        context = {
            'user': form.instance,
            'confirm_email_url': confirm_url
        }
        engine = template.engines['django']
        email = EmailMessage(
            subject=engine.from_string(settings.REGISTRATION_SUBJECT_PATH.read_text('UTF-8')).render(context),
            body=engine.from_string(settings.REGISTRATION_BODY_PATH.read_text('UTF-8')).render(context),
            to=[form.instance.email],
            from_email=settings.REGISTRATION_FROM_EMAIL or settings.DEFAULT_FROM_EMAIL
        )
        email.send()
        return response


class ConfirmEMailView(TemplateView):
    template_name = 'accounts/confirm_email.html'
    success: bool = False

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['success'] = True
        return context_data

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        uid = force_str(urlsafe_base64_decode(kwargs['uidb64']))
        try:
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, _('Could not find your user.'))
            return super().get(request, *args, **kwargs)

        if email_confirm_token_generator.check_token(user, kwargs['token']):
            user.is_active = True
            user.save()
            messages.success(request, _('Your EMail was confirmed. You can now login.'))
            self.success = True
        else:
            messages.error(request, _('Your activation link was invalid.'))
        return super().get(request, *args, **kwargs)


class UserEditView(BaseLoginMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('user_profile')

    def get_object(self):
        return self.request.user


class UserDeleteSelfView(BaseLoginMixin, View):

    def delete(self, request, *args, **kwargs):
        if request.POST.get('confirm') != 'true':
            messages.error(self.request, _('Error while deleting your data: Please confirm deletion!'))
            return HttpResponseRedirect(self.request.user.get_absolute_url())
        self.request.user.delete()
        auth_logout(self.request)
        return HttpResponseRedirect(settings.LOGIN_URL)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
