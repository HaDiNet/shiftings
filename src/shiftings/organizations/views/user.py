from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from shiftings.organizations.models import Organization, OrganizationDummyUser
from shiftings.organizations.views.organization_base import OrganizationMemberMixin, OrganizationPermissionMixin
from shiftings.utils.exceptions import Http403
from shiftings.utils.views.create_update_view import CreateOrUpdateView


class ClaimUserListView(OrganizationMemberMixin, ListView):
    template_name = 'organizations/user/claim_users.html'
    model = OrganizationDummyUser
    context_object_name = 'users'

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'org_pk')

    def get_queryset(self) -> QuerySet[OrganizationDummyUser]:
        return OrganizationDummyUser.objects.filter(organization=self.get_organization())


class ClaimUserView(OrganizationMemberMixin, CreateOrUpdateView[OrganizationDummyUser]):
    http_method_names = 'post'
    model = OrganizationDummyUser
    fields = ['claimed_by']

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'org_pk')

    def form_valid(self, form: ModelForm) -> HttpResponse:
        if form.instance.claimed_by is not None:
            raise Http403(_('You can\'t claim users that are already claimed.'))
        form.instance.claimed_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('claim_user_list', args=[self.get_organization().pk])


class UnclaimUserView(OrganizationPermissionMixin, CreateOrUpdateView[OrganizationDummyUser]):
    permission_required = 'organizations.admin'
    http_method_names = 'post'
    model = OrganizationDummyUser
    fields = ['claimed_by']

    def get_organization(self) -> Organization:
        return self._get_object(Organization, 'org_pk')

    def form_valid(self, form: ModelForm) -> HttpResponse:
        form.instance.claimed_by = None
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('claim_user_list', args=[self.get_organization().pk])
