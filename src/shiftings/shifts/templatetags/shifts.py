from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Optional

from django import template
from django.db.models import Count, Q
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
    shifts_in_range = org.shifts.filter(time_filter)
    context['groups'] = groups
    context['has_others'] = shifts_in_range.filter(other_filter).exists()
    org_users_only = get_bool('org_users_only', False)

    participant_ids = set(shifts_in_range.values_list('participants__user', flat=True))
    participant_ids.discard(None)

    # Resolve participants to either direct users, unclaimed org dummy users, or their claimed-by users.
    participant_user_ids = set(User.objects.filter(pk__in=participant_ids).values_list('pk', flat=True))
    participant_dummy_users = OrganizationDummyUser.objects.filter(pk__in=participant_ids).values('pk', 'claimed_by_id')
    claimed_dummy_ids = []
    for dummy_user in participant_dummy_users:
        if dummy_user['claimed_by_id'] is None:
            participant_user_ids.add(dummy_user['pk'])
        else:
            claimed_dummy_ids.append(dummy_user['claimed_by_id'])
    claimed_ids = set(claimed_dummy_ids)
    participant_user_ids.update(BaseUser.objects.filter(pk__in=claimed_ids).values_list('pk', flat=True))

    org_user_ids = set(org.users.values_list('pk', flat=True))

    if org_users_only:
        users = BaseUser.objects.filter(pk__in=org_user_ids)
    elif show_all_users:
        users = BaseUser.objects.filter(pk__in=participant_user_ids)
    else:
        users = BaseUser.objects.filter(pk__in=(participant_user_ids | org_user_ids))

    participant_to_user_id = {pk: pk for pk in participant_user_ids}
    for dummy_user in OrganizationDummyUser.objects.filter(pk__in=participant_ids).values('pk', 'claimed_by_id'):
        participant_to_user_id[dummy_user['pk']] = dummy_user['claimed_by_id'] or dummy_user['pk']

    grouped_counts: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    group_ids = [group.pk for group in groups]
    for row in shifts_in_range.filter(
        participants__user__pk__in=participant_ids,
        shift_type__group__pk__in=group_ids,
    ).values('participants__user__pk', 'shift_type__group__pk').annotate(total=Count('pk', distinct=True)):
        effective_user_id = participant_to_user_id.get(row['participants__user__pk'])
        if effective_user_id is None:
            continue
        grouped_counts[effective_user_id][row['shift_type__group__pk']] += row['total']

    other_counts: dict[int, int] = defaultdict(int)
    for row in shifts_in_range.filter(
        other_filter,
        participants__user__pk__in=participant_ids,
    ).values('participants__user__pk').annotate(total=Count('pk', distinct=True)):
        effective_user_id = participant_to_user_id.get(row['participants__user__pk'])
        if effective_user_id is None:
            continue
        other_counts[effective_user_id] += row['total']

    member_entries = []
    for user in users.order_by('username'):
        group_amounts = [grouped_counts[user.pk].get(shift_type_group.pk, 0) for shift_type_group in groups]
        others_amount = other_counts.get(user.pk, 0)
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
