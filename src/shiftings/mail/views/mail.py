from typing import Any, Optional

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from shiftings.accounts.models import User
from shiftings.mail.forms.mail import MailForm
from shiftings.utils.typing import UserRequest
from shiftings.utils.views.base import BaseLoginMixin


class BaseMailView(BaseLoginMixin, FormView):
    request: UserRequest

    template_name = 'mail/mail.html'
    form_class = MailForm
    form_params: Optional[dict[str, Any]] = {'enctype': 'multipart/form-data'}

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['replacements'] = self.get_replacements()
        context['users'] = self.get_users()
        context['form_params'] = self.form_params
        return context

    def get_replacements(self) -> dict[str, str]:
        return {'me': self.request.user.display}

    def form_valid(self, form: MailForm) -> HttpResponse:
        replacements = self.get_replacements()
        subject = form.cleaned_data['subject'].format(**replacements)
        text = form.cleaned_data['text'].format(**replacements)
        users = self.get_users(form)
        email = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email for user in users],
                             headers={'Reply-To': settings.DEFAULT_FROM_EMAIL})
        for file in dict(form.files).get('attachments', list()):
            email.attach(file.name, file.file.read(), mimetype=file.content_type)
        email.send()
        messages.success(self.request, _('E-Mail sent to {count} user(s).').format(count=users.count()))
        return HttpResponseRedirect(self.get_success_url())

    def get_users(self, form: Optional[MailForm] = None) -> QuerySet[User]:
        return QuerySet()
