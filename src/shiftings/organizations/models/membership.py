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
        permissions = [
            # organization
            ('edit_organization', _('edit organization details')),
            ('see_members', _('see members of the organization')),
            ('see_statistics', _('see shift participation statistics')),
            ('send_mail', _('send emails to everyone in the organization')),
            # membership
            ('edit_membership_types', _('create and update membership types for the organization')),
            ('edit_members', _('add and remove members for the organization')),
            # events
            ('edit_events', _('create and update events for the organization')),
            # shifts
            ('edit_recurring_shifts', _('create and update recurring shifts for the organization')),
            ('edit_shift_templates', _('create and update shifts templates for the organization')),
            ('edit_shifts', _('create and update shifts for the organization')),
            # shift participation
            ('remove_others_from_shifts', _('remove others from shifts')),
            ('add_non_members_to_shifts', _('add other users that are not members of the organization to shifts')),
            ('add_members_to_shifts', _('add other organization members to shifts')),
            ('participate_in_shift', _('participate in shifts')),
        ]
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
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='members')
    type = models.ForeignKey('MembershipType', on_delete=models.CASCADE, verbose_name=_('Membership Type'),
                             related_name='memberships')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='memberships',
                             verbose_name=_('User'), blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships', verbose_name=_('Group'),
                              blank=True, null=True)

    class Meta:
        default_permissions = ()
        ordering = ['type', 'group', 'user']
        constraints = [
            UniqueConstraint(fields=['organization', 'type', 'user'], name='unique_membership_organization_type_user'),
            UniqueConstraint(fields=['organization', 'type', 'group'],
                             name='unique_membership_organization_type_group'),
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
