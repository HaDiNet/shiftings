from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _


class MembershipType(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='membership_types')
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    admin = models.BooleanField(verbose_name=_('Admin'), default=None, blank=True, null=True)
    default = models.BooleanField(verbose_name=_('Default'), default=None, blank=True, null=True)
    permissions = models.ManyToManyField(Permission, verbose_name=_('Permissions'), blank=True)

    class Meta:
        default_permissions = ()
        ordering = ['organization', '-admin', '-default', 'name']
        constraints = [
            UniqueConstraint(fields=['organization', 'name'], name='name_unique_per_organization'),
            UniqueConstraint(fields=['organization', 'admin'], name='admin_unique_per_organization'),
            UniqueConstraint(fields=['organization', 'default'], name='default_unique_per_organization'),
            CheckConstraint(check=~Q(admin=False), name='admin_true_or_null'),
            CheckConstraint(check=~Q(default=False), name='default_true_or_null'),
            CheckConstraint(check=(Q(admin=True, default__isnull=True) | Q(admin__isnull=True)),
                            name='admin_not_default')
        ]

    def __str__(self) -> str:
        return self.display

    @property
    def display(self) -> str:
        if self.admin:
            return _('{name} (Admin)').format(name=self.name)
        if self.default:
            return _('{name} (Default)').format(name=self.name)
        return self.name


class Membership(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='all_members')
    type = models.ForeignKey('MembershipType', on_delete=models.CASCADE, verbose_name=_('Membership Type'),
                             related_name='memberships')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='memberships',
                             verbose_name=_('User'), blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships', verbose_name=_('Group'),
                              blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['type', 'group', 'user']
        constraints = [UniqueConstraint(fields=['user', 'organization'], name='unique_user_organization'),
                       UniqueConstraint(fields=['group', 'organization'], name='unique_group_organization'),
                       CheckConstraint(check=(~(Q(user__isnull=True) & Q(group__isnull=True))), name='group_or_user')
                       ]

    def __str__(self) -> str:
        return f'{self.user.display if self.user else self.group.name}'

    @property
    def is_user(self) -> bool:
        return self.user is not None

    @property
    def user_pks(self) -> list[int]:
        if self.is_user:
            return [self.user.pk]
        return list(self.group.user_set.values_list('pk', flat=True))

    def is_member(self, user):
        return self.user == user or self.group in user.groups.all()

    def clean(self) -> None:
        if self.user and self.group:
            raise ValidationError(_('Membership can only be either user or group, not both.'))
        if not self.user and not self.group:
            raise ValidationError(_('Membership must consist of a user or a group.'))
