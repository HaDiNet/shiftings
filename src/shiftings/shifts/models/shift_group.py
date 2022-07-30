from django.db import models
from django.utils.translation import gettext_lazy as _


class ShiftGroup(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     related_name='shift_groups')
    position = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100, verbose_name=_('Group Name'))
    shift_types = models.ManyToManyField('ShiftType', verbose_name=_('Shift Types'))

    class Meta:
        default_permissions = ()
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'position'], name='shift_group_position_unique_constraint'),
            models.UniqueConstraint(fields=['organization', 'name'], name='shift_group_name_unique_constraint')
        ]
