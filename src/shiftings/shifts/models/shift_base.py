from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class ShiftBase(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    place = models.CharField(max_length=100, verbose_name=_('Place'), blank=True, null=True)

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='%(class)ss',
                                     verbose_name=_('Organization'))
    shift_group = models.ForeignKey('ShiftGroup', verbose_name=_('Shift Group'), on_delete=models.SET_NULL, blank=True,
                                    null=True)

    required_users = models.PositiveIntegerField(verbose_name=_('Required User'), default=0)
    max_users = models.PositiveIntegerField(verbose_name=_('Maximum User'), default=0)

    additional_infos = models.TextField(verbose_name=_('Additional Infos'), blank=True, null=True)

    class Meta:
        abstract = True
        default_permissions = ()
        constraints = [
            models.CheckConstraint(check=Q(max_users=0) | Q(max_users__gte=F('required_users')),
                                   name='shift_max_users_gte_required_users')
        ]
