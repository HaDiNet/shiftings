from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, DetailView

from shiftings.accounts.forms.user_form import UserCreateForm
from shiftings.accounts.models import Shifter


class ShifterProfileView(DetailView):
    model = Shifter

    def get_object(self, queryset = None):
        if self.kwargs.get(self.pk_url_kwarg) is None:
            return self.request.user
        return super().get_object(queryset)


@method_decorator(sensitive_post_parameters('password', 'confirm_password'), name='dispatch')
class ShifterCreateView(CreateView):
    model = Shifter
    form_class = UserCreateForm
    success_url = reverse_lazy('user_profile')

    def form_valid(self, form: UserCreateForm) -> HttpResponse:
        form.instance.password = make_password(form.cleaned_data.get('password'))
        form.save()
        return super().form_valid(form)
