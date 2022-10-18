from datetime import date
from typing import Any

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, DetailView, UpdateView

from shiftings.accounts.forms.user_form import UserCreateForm, UserUpdateForm
from shiftings.accounts.models import User
from shiftings.shifts.models import Shift
from shiftings.utils.pagination import get_pagination_context
from shiftings.utils.views.base import BaseLoginMixin


class UserProfileView(BaseLoginMixin, DetailView):
    model = User
    object: User

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = date.today()
        shifts = Shift.objects.filter(Q(start__date__gte=today) &
                                      (Q(event__in=self.object.events) |
                                       Q(organization__in=self.object.organizations)))
        context['shifts'] = get_pagination_context(self.request, shifts, 5, 'shifts')
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
        form.instance.password = make_password(form.cleaned_data.get('password'))
        form.save()
        return super().form_valid(form)


class UserEditView(BaseLoginMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('user_profile')

    def get_object(self):
        return self.request.user
