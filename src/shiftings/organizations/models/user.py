from django.db import models

from shiftings.accounts.models.user import BaseUser


class OrganizationDummyUser(BaseUser):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()
