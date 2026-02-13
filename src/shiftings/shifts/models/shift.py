from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shiftings.utils.fields.date_time import DateTimeField
from .base import ShiftBase
from .permission import ParticipationPermission, ParticipationPermissionType

if TYPE_CHECKING:
    from shiftings.accounts.models import User


class Shift(ShiftBase):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='shifts', verbose_name=_('Event'),
                              blank=True, null=True)

    start = DateTimeField(verbose_name=_('Start Date and Time'), db_index=True)
    end = DateTimeField(verbose_name=_('End Date and Time'), db_index=True)

    participants = models.ManyToManyField('shifts.Participant', verbose_name=_('Users'), blank=True,
                                          related_name='shift_set')

    locked = models.BooleanField(verbose_name=_('Locked for Participation'), default=False)
    warnings = models.TextField(max_length=500, verbose_name=_('Warning'), blank=True, null=True,
                                help_text=_('A maximum of {amount} characters is allowed').format(amount=500))

    based_on = models.ForeignKey('RecurringShift', on_delete=models.SET_NULL, related_name='created_shifts',
                                 verbose_name=_('Created by Recurring Shift'), blank=True, null=True)

    created = DateTimeField(verbose_name=_('Created'), auto_now_add=True)
    modified = DateTimeField(verbose_name=_('Last Modified'), auto_now=True)

    participation_permissions = GenericRelation('ParticipationPermission',
                                                content_type_field='referred_content_type',
                                                object_id_field='referred_object_id',
                                                related_query_name='ref_shift')

    class Meta:
        default_permissions = ()
        ordering = ['start', 'end', 'name', 'organization']
        constraints = [
            models.CheckConstraint(condition=Q(start__lte=F('end')), name='shift_start_before_end')
        ]

    def clean(self) -> None:
        if self.event and self.event.organization != self.organization:
            raise ValidationError(_('Organization and Event Organization must be identical.'))

    def __str__(self) -> str:
        return _('Shift {name} on {time}').format(name=self.name, time=self.start.strftime('%Y-%m-%d %H:%M:%S'), )

    @property
    def display(self) -> str:
        return self.name

    @property
    def detailed_display(self) -> str:
        return _('{name} from {start} to {end} ').format(name=self.name,
                                                         start=self.start.strftime('%Y-%m-%d %H:%M'),
                                                         end=self.end.strftime('%Y-%m-%d %H:%M'))

    @property
    def time_display(self) -> str:
        if self.start.date() != self.end.date():
            return _('{start} to {end_time} on {end_date}').format(name=self.name,
                                                                    start=self.start.strftime('%H:%M'),
                                                                    end_time=self.end.strftime('%H:%M'),
                                                                    end_date=self.end.date())
        return _('{start} to {end_time}').format(name=self.name,
                                                 start=self.start.strftime('%H:%M'),
                                                 end_time=self.end.strftime('%H:%M'), )

    @property
    def is_full(self) -> bool:
        return self.max_users != 0 and self.participants.all().count() >= self.max_users

    @property
    def participants_missing(self) -> int:
        if self.max_users == 0:
            return 0
        return max(self.max_users - self.participants.all().count(), 0)

    @property
    def has_required(self) -> bool:
        return self.participants.all().count() >= self.required_users

    @property
    def required_participants_missing(self) -> int:
        if self.required_users == 0:
            return 0
        return max(self.required_users - self.participants.all().count(), 0)

    @property
    def confirmed_participants(self) -> Optional[int]:
        if not self.organization.confirm_participation_active:
            return None
        return self.participants.all().count() - self.participants.filter(confirmed=True).count()

    @property
    def email(self) -> str:
        if self.event and self.event.email:
            return self.event.email
        return self.organization.email

    @property
    def inherited_participation_permissions(self) -> QuerySet[ParticipationPermission]:
        return ParticipationPermission.objects.filter_instances(self.event, self.organization)

    def get_slots_display(self) -> Optional[list[tuple[Union[bool, User], bool]]]:
        slots = []
        if self.required_users != 0:
            slots = [(False, True)] * self.required_users
        if self.max_users != 0:
            slots += [(False, False)] * (self.max_users - self.required_users)
        for i, user in enumerate(self.participants.all().order_by('pk')):
            try:
                slots[i] = user, slots[i][1]
            except IndexError:
                slots.append((user, False))
        return slots

    def is_participant(self, user: User) -> bool:
        return self.participants.filter(user=user).exists()

    def get_user_permission(self, user):
        if user.has_perm('organizations.participate_in_shift', self.organization):
            return ParticipationPermissionType.Participate
        return ParticipationPermission.objects.get_best_for_user(user, self, self.event, self.organization)

    def can_see(self, user: User) -> bool:
        if self.is_participant(user) or self.organization.is_member(user):
            return True
        return self.get_user_permission(user) >= ParticipationPermissionType.Existence

    def can_see_details(self, user: User) -> bool:
        if self.is_participant(user) or self.organization.is_member(user):
            return True
        return self.get_user_permission(user) >= ParticipationPermissionType.ShiftDetails

    def can_see_participants(self, user: User) -> bool:
        if self.is_participant(user) or self.organization.is_member(user):
            return True
        return self.get_user_permission(user) >= ParticipationPermissionType.ShiftParticipants

    def can_participate(self, user: User) -> bool:
        if self.is_participant(user):
            return False
        return self.get_user_permission(user) >= ParticipationPermissionType.Participate

    def get_absolute_url(self) -> str:
        return reverse('shift', args=[self.pk])
