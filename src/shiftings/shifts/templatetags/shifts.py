from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Optional

from django import template
from django.db.models import Q
from django.utils.translation import gettext as _

from shiftings.accounts.models import BaseUser, User
from shiftings.organizations.models import OrganizationDummyUser
from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.shifts.forms.shift import SelectOrgForm
from shiftings.shifts.models import Shift
from shiftings.utils.time.timerange import TimeRangeType

register = template.Library()


@register.inclusion_tag('shifts/template/shift_card.html', takes_context=True)
def shift_card(context, shift) -> dict[str, Any]:
    context.update({
        'shift': shift,
        'organization': shift.organization,
        'current_date': date.today(),
        'add_self_form': AddSelfParticipantForm(shift, initial={'user': context['request'].user}),
        'user_is_participant': shift.is_participant(context['request'].user),
    })
    return context


@register.inclusion_tag('shifts/template/shift_users_summary.html', takes_context=True)
def shift_users_summary(context, org, show_all_users: bool = False, show_future_shifts: bool = True) -> dict[str, Any]:
    def get_int(name: str, default: int) -> int:
        try:
            return int(context['request'].GET.get(name, default))
        except ValueError:
            return default

    def get_bool(name: str, default: bool = False) -> bool:
        value = context['request'].GET.get(name)
        if value is None:
            return default
        return value.lower() in {'1', 'true', 'yes', 'on'}

    try:
        time_range_type = TimeRangeType(get_int('time_range', org.summary_settings.default_time_range_type))
    except ValueError:
        time_range_type = org.summary_settings.default_time_range
    year = get_int('year', date.today().year)
    month = get_int('month', date.today().month)
    time_range = time_range_type.get_time_range(year, month)
    time_filter = Q(start__range=time_range) | Q(end__range=time_range)
    if not show_future_shifts:
        time_filter &= Q(start__lte=date.today())
    other_filter = Q(shift_type__isnull=True) | Q(shift_type__group__isnull=True)
    groups = list(org.shift_type_groups.all())
    context['groups'] = groups
    context['has_others'] = org.shifts.filter(time_filter, other_filter).exists()
    org_users_only = get_bool('org_users_only', False)

    participant_ids = set(org.shifts.filter(time_filter).values_list('participants__user', flat=True))
    participant_ids.discard(None)

    # Resolve participants to either direct users, unclaimed org dummy users, or their claimed-by users.
    participant_user_ids = set(User.objects.filter(pk__in=participant_ids).values_list('pk', flat=True))
    participant_dummy_users = OrganizationDummyUser.objects.filter(pk__in=participant_ids)
    participant_user_ids.update(participant_dummy_users.filter(claimed_by__isnull=True).values_list('pk', flat=True))
    claimed_ids = participant_dummy_users.filter(claimed_by__isnull=False).values_list('claimed_by__pk', flat=True)
    participant_user_ids.update(BaseUser.objects.filter(pk__in=claimed_ids).values_list('pk', flat=True))

    org_user_ids = set(org.users.values_list('pk', flat=True))

    if org_users_only:
        users = BaseUser.objects.filter(pk__in=org_user_ids)
    elif show_all_users:
        users = BaseUser.objects.filter(pk__in=participant_user_ids)
    else:
        users = BaseUser.objects.filter(pk__in=(participant_user_ids | org_user_ids))
    member_entries = []
    for user in users.order_by('username'):
        pks = [user.pk] + list(OrganizationDummyUser.objects.filter(claimed_by=user).values_list('pk', flat=True))
        group_amounts = [
            org.shifts.filter(time_filter, participants__user__pk__in=pks, shift_type__group=shift_type_group).count()
            for shift_type_group in groups
        ]
        others_amount = org.shifts.filter(time_filter, other_filter, participants__user__pk__in=pks).count()
        member_entries.append({
            'pk': user.pk,
            'name': user.display,
            'is_org_user': user.pk in org_user_ids,
            'groups': group_amounts,
            'other': others_amount,
            'total': sum(group_amounts) + others_amount
        })

    participants = [member for member in member_entries if member['total'] > 0]
    participants.sort(key=lambda member: (-member['total'], member['name']))

    if show_all_users:
        context['members'] = participants
        context['other_users'] = []
        context['other_users_count'] = 0
        context['has_other_users_section'] = False
    else:
        context['members'] = participants
        other_users = [member for member in member_entries if member['is_org_user'] and member['total'] == 0]
        context['other_users'] = other_users
        context['other_users_count'] = len(other_users)
        context['has_other_users_section'] = len(other_users) > 0

    context['other_participants'] = []
    context['has_other_participants_section'] = False
    context['show_all_users'] = show_all_users
    context['org_users_only'] = org_users_only
    return context


@register.simple_tag()
def calculate_shift_time(shift_time: time, start_delay: timedelta, shift_duration: Optional[timedelta] = None) -> str:
    delta = start_delay
    if shift_duration is not None:
        delta += shift_duration
    format_str = f'%H:%M'
    if delta.days > 0:
        format_str += _('Days + {delta_days}').format(delta_days=delta.days)
    return (datetime.combine(date.today(), shift_time) + delta).time().strftime(format_str)


@register.inclusion_tag('shifts/template/select_org.html', takes_context=True)
def select_org_form_modal(context: dict[str, Any]):
    context['form'] = SelectOrgForm(context['request'].user)
    return context


@register.inclusion_tag('shifts/template/small_shift_display.html', takes_context=True)
def small_shift_display(context, shift) -> dict[str, Any]:
    if shift.is_full:
        status_class = 'border-success'
    elif shift.has_required:
        status_class = 'border-warning'
    else:
        status_class = 'border-danger'
    context.update({
        'shift': shift,
        'organization': shift.organization,
        'current_date': date.today(),
        'user_is_participant': shift.is_participant(context['request'].user),
        'shift_status_border': status_class
    })
    return context


@dataclass
class ShiftPermissionHolder:
    shift: Shift
    user: User

    def can_see(self) -> bool:
        return self.shift.can_see(self.user)

    def can_see_details(self) -> bool:
        return self.shift.can_see_details(self.user)

    def can_see_participants(self) -> bool:
        return self.shift.can_see_participants(self.user)

    def can_participate(self) -> bool:
        return self.shift.can_participate(self.user)


@register.simple_tag(takes_context=True)
def shift_permissions(context, shift: Shift) -> ShiftPermissionHolder:
    return ShiftPermissionHolder(shift, context.request.user)
