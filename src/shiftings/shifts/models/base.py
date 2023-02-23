from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class ShiftBase(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    place = models.CharField(max_length=100, verbose_name=_('Place'), blank=True, null=True)

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='%(class)ss',
                                     verbose_name=_('Organization'))
    shift_type = models.ForeignKey('ShiftType', verbose_name=_('Shift Type'), on_delete=models.SET_NULL, blank=True,
                                   null=True)

    required_users = models.PositiveSmallIntegerField(verbose_name=_('Required Users'), default=0,
                                                      validators=[MaxValueValidator(32)],
                                                      help_text=_('A maximum of 32 users can be required'))
    max_users = models.PositiveSmallIntegerField(verbose_name=_('Maximum Users'), default=0,
                                                 validators=[MaxValueValidator(64)],
                                                 help_text=_('A maximum of 64 users can be present'))

    additional_infos = models.TextField(max_length=1000, verbose_name=_('Additional Infos'), blank=True, null=True,
                                        help_text=_('A maximum of {amount} characters is allowed').format(amount=1000))

    class Meta:
        abstract = True
        default_permissions = ()
        constraints = [
            models.CheckConstraint(check=Q(max_users=0) | Q(max_users__gte=F('required_users')),
                                   name='shift_max_users_gte_required_users')
        ]
