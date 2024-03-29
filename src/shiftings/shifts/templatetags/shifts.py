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


@register.inclusion_tag('shifts/template/member_shift_summary.html', takes_context=True)
def member_shift_summary(context, org, show_all_users: bool = False, show_future_shifts: bool = True) -> dict[str, Any]:
    def get_int(name: str, default: int) -> int:
        try:
            return int(context['request'].GET.get(name, default))
        except ValueError:
            return default

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
    users = org.users
    if show_all_users:
        user_ids = set(org.shifts.filter(time_filter).values_list('participants__user', flat=True))
        user_ids.discard(None)
        filtered_user_ids = set(User.objects.filter(pk__in=user_ids).values_list('pk', flat=True))
        filtered_dummy_users = OrganizationDummyUser.objects.filter(pk__in=user_ids)
        filtered_user_ids.update(filtered_dummy_users.filter(claimed_by__isnull=True).values_list('pk', flat=True))
        claimed_ids = filtered_dummy_users.filter(claimed_by__isnull=False).values_list('claimed_by__pk', flat=True)
        filtered_user_ids.update(BaseUser.objects.filter(pk__in=claimed_ids).values_list('pk', flat=True))
        users = BaseUser.objects.filter(pk__in=filtered_user_ids)
    members = []
    for user in users.order_by('username'):
        pks = [user.pk] + list(OrganizationDummyUser.objects.filter(claimed_by=user).values_list('pk', flat=True))
        group_amounts = [
            org.shifts.filter(time_filter, participants__user__pk__in=pks, shift_type__group=shift_type_group).count()
            for shift_type_group in groups
        ]
        others_amount = org.shifts.filter(time_filter, other_filter, participants__user__pk__in=pks).count()
        members.append({
            'pk': user.pk,
            'name': user.display,
            'groups': group_amounts,
            'other': others_amount,
            'total': sum(group_amounts) + others_amount
        })
    members.sort(key=lambda member: -member['total'])
    context['members'] = members
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
