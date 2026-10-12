from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizationMemberNote(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='member_notes',
                                     verbose_name=_('Organization'))
    user = models.ForeignKey('accounts.BaseUser', on_delete=models.CASCADE, related_name='organization_notes',
                             verbose_name=_('User'))
    note = models.TextField(verbose_name=_('Note'), blank=True, default='')

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(fields=['organization', 'user'], name='unique_org_member_note')
        ]

    def __str__(self) -> str:
        return f'{self.organization} - {self.user.display}'
