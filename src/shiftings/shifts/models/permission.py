from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, QuerySet, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from shiftings.accounts.models import User
from shiftings.organizations.models import Organization


class ParticipationPermissionType(models.IntegerChoices):
    NoPermission = 0, _('Nothing')
    Existence = 1, _('See Shift exists')
    ShiftDetails = 2, _('See Shift Details')
    ShiftParticipants = 3, _('See Shift Participants')
    Participate = 4, _('Participate')


class ParticipationPermissionManager(models.Manager):
    def create_for_instance(self, instance: models.Model, **kwargs: Any) -> ParticipationPermission:
        return self.create(referred_content_type=ContentType.objects.get_for_model(instance),
                           referred_object_id=instance.pk, **kwargs)

    def filter_instance(self, instance: models.Model) -> QuerySet[ParticipationPermission]:
        if instance is None:
            return self.none()
        return self.filter(referred_content_type=ContentType.objects.get_for_model(instance),
                           referred_object_id=instance.pk)

    def filter_instances(self, *instances: models.Model) -> QuerySet[ParticipationPermission]:
        query = Q()
        for instance in instances:
            if instance is not None:
                query |= Q(referred_content_type=ContentType.objects.get_for_model(instance),
                           referred_object_id=instance.pk)
        return self.filter(query)

    def get_for_instance(self, instance: models.Model,
                         organization: Organization | None) -> ParticipationPermission | None:
        return self.filter_instance(instance).filter(organization=organization).first()

    def get_best_for_instance_and_user(self, instance: models.Model, user: User) -> ParticipationPermissionType:
        if user.has_perm('organizations.admin'):
            return ParticipationPermissionType.Participate
        best_permission = self.filter_instance(instance) \
            .filter(Q(organization__isnull=True) | Q(organization__in=user.organizations)) \
            .aggregate(best=models.Max('permission_type_field'))['best']
        if not best_permission:
            return ParticipationPermissionType.NoPermission
        return ParticipationPermissionType(best_permission)

    def get_best_for_user(self, user: User, *objects: models.Model) -> ParticipationPermissionType:
        if user.has_perm('organizations.admin'):
            return ParticipationPermissionType.Participate
        best_permission = self.filter_instances(*objects) \
            .filter(Q(organization__isnull=True) | Q(organization__in=user.organizations)) \
            .aggregate(best=models.Max('permission_type_field'))['best']
        if not best_permission:
            return ParticipationPermissionType.NoPermission
        return ParticipationPermissionType(best_permission)


class ParticipationPermission(models.Model):
    referred_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    referred_object_id = models.BigIntegerField()
    referred_object = GenericForeignKey('referred_content_type', 'referred_object_id')

    permission_type_field = models.PositiveSmallIntegerField(choices=ParticipationPermissionType.choices,
                                                             verbose_name=_('Permission Type'))
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     verbose_name=_('Affected Organization'), related_name='participation_permissions',
                                     blank=True, null=True)

    objects = ParticipationPermissionManager()

    class Meta:
        default_permissions = ()
        indexes = [
            models.Index(fields=['referred_content_type', 'referred_object_id'], name='referred_object_index')
        ]
        constraints = [
            UniqueConstraint(fields=['referred_content_type', 'referred_object_id', 'organization'],
                             name='organization_unique_per_referred_object')
        ]

    @property
    def permission_type(self) -> ParticipationPermissionType:
        return ParticipationPermissionType(self.permission_type_field)
