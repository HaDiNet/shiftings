from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Membership(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='all_members')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='memberships',
                             verbose_name=_('User'), blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships', verbose_name=_('Group'),
                              blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['group', 'user']

    def __str__(self) -> str:
        return self.user.name if self.user else self.group.name

    @property
    def is_user(self) -> bool:
        return self.user is not None

    def clean(self) -> None:
        if self.user and self.group:
            raise ValidationError(_('Membership can only be either user or group, not both.'))
        if not self.user and not self.group:
            raise ValidationError(_('Membership must consist of a user or a group.'))
