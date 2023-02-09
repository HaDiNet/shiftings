from django.db import models
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models.user import BaseUser


class OrganizationDummyUser(BaseUser):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    claimed_by = models.ForeignKey('accounts.BaseUser', on_delete=models.SET_NULL,
                                   related_name='claimed_org_dummy_users', verbose_name=_('Claimed by'), blank=True,
                                   null=True, default=None)

    class Meta:
        default_permissions = ()

    def can_be_claimed(self) -> bool:
        if self.claimed_by is not None:
            return False
        if OrganizationDummyUser.objects.filter(claimed_by=self).exists():
            return False
        return True
