from datetime import date
from typing import Any

from django import template
from django.db.models import Q

from shiftings.shifts.forms.participant import AddSelfParticipantForm
from shiftings.utils.time.timerange import TimeRangeType

register = template.Library()


@register.inclusion_tag('shifts/template/shift_card.html', takes_context=True)
def shift_card(context, shift) -> dict[str, Any]:
    context['shift'] = shift
    context['add_self_form'] = AddSelfParticipantForm(shift, initial={'user': context['request'].user})
    return context


@register.inclusion_tag('shifts/template/member_shift_summary.html', takes_context=True)
def member_shift_summary(context, org) -> dict[str, Any]:
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
    types = list(org.shift_types.all())
    context['groups'] = types
    context['has_other'] = org.shifts.filter(time_filter, shift_type__isnull=True).exists()
    context['members'] = [{
        'name': member.user.display,
        'groups': [org.shifts.filter(time_filter, participants__user=member.user,
                                     shift_type=shift_type).count()
                   for shift_type in types],
        'other': org.shifts.filter(time_filter, shift_type__isnull=True, participants__user=member.user).count()
    } for member in org.all_members.all().order_by('user__username')]
    return context
