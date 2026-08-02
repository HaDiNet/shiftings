from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase

from shiftings.accounts.models import User
from shiftings.shifts.forms.participant import AddOtherParticipantForm, AddSelfParticipantForm
from shiftings.shifts.forms.recurring import RecurringShiftForm
from shiftings.shifts.forms.shift import ShiftForm
from shiftings.shifts.forms.template import ShiftTemplateForm
from shiftings.shifts.models import Participant, Shift, ShiftTemplateGroup, ShiftType
from shiftings.shifts.models.recurring import ProblemHandling
from shiftings.shifts.utils.time_frame import TimeFrameType
from shiftings.organizations.models import Organization
from shiftings.utils.time.week import WeekDay


class ShiftFormTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.shift_type = ShiftType.objects.filter(organization=self.organization).first()

    def test_valid_shift_data_passes_validation(self) -> None:
        form = ShiftForm(
            instance=Shift(organization=self.organization, shift_type=self.shift_type),
            data={
                'name': 'Morning shift',
                'place': 'K1 Bar',
                'organization': self.organization.pk,
                'event': '',
                'shift_type': self.shift_type.pk,
                'start': '2024-01-01 10:00:00',
                'end': '2024-01-01 12:00:00',
                'required_users': 1,
                'max_users': 2,
                'additional_infos': '',
                'locked': False,
            },
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start'].hour, 10)
        self.assertEqual(form.cleaned_data['end'].hour, 12)

    def test_shift_end_before_start_is_rejected(self) -> None:
        form = ShiftForm(
            instance=Shift(organization=self.organization, shift_type=self.shift_type),
            data={
                'name': 'Broken shift',
                'place': 'K1 Bar',
                'organization': self.organization.pk,
                'event': '',
                'shift_type': self.shift_type.pk,
                'start': '2024-01-01 12:00:00',
                'end': '2024-01-01 10:00:00',
                'required_users': 1,
                'max_users': 2,
                'additional_infos': '',
                'locked': False,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('start', form.errors)
        self.assertIn('end', form.errors)

    def test_invalid_datetimes_do_not_crash_clean(self) -> None:
        form = ShiftForm(
            instance=Shift(organization=self.organization, shift_type=self.shift_type),
            data={
                'name': 'Broken datetime shift',
                'place': 'K1 Bar',
                'organization': self.organization.pk,
                'event': '',
                'shift_type': self.shift_type.pk,
                'start': 'invalid-start',
                'end': 'invalid-end',
                'required_users': 1,
                'max_users': 2,
                'additional_infos': '',
                'locked': False,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('start', form.errors)
        self.assertIn('end', form.errors)


class RecurringShiftFormTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.template_group = ShiftTemplateGroup.objects.get(pk=1)

    def test_weekly_recurring_shift_validates(self) -> None:
        form = RecurringShiftForm(
            data={
                'name': 'Weekly bar shift',
                'organization': self.organization.pk,
                'time_frame_field': TimeFrameType.EveryNthWeekday.value,
                'ordinal': 2,
                'week_day_field': WeekDay.Monday.value,
                'month_field': '',
                'first_occurrence': '2024-01-01',
                'auto_create_days': 7,
                'color': '#FD7E14',
                'template': self.template_group.pk,
                'weekend_handling_field': ProblemHandling.Ignore.value,
                'weekend_warning': '',
                'holiday_handling_field': ProblemHandling.Ignore.value,
                'holiday_warning': '',
            },
            initial={'organization': self.organization},
        )

        self.assertTrue(form.is_valid())

    def test_weekday_timeframe_requires_weekday(self) -> None:
        form = RecurringShiftForm(
            data={
                'name': 'Weekly bar shift',
                'organization': self.organization.pk,
                'time_frame_field': TimeFrameType.EveryNthWeekday.value,
                'ordinal': 2,
                'week_day_field': '',
                'month_field': '',
                'first_occurrence': '2024-01-01',
                'auto_create_days': 7,
                'color': '#FD7E14',
                'template': self.template_group.pk,
                'weekend_handling_field': ProblemHandling.Ignore.value,
                'weekend_warning': '',
                'holiday_handling_field': ProblemHandling.Ignore.value,
                'holiday_warning': '',
            },
            initial={'organization': self.organization},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('week_day_field', form.errors)

    def test_month_timeframe_requires_month(self) -> None:
        form = RecurringShiftForm(
            data={
                'name': 'Monthly bar shift',
                'organization': self.organization.pk,
                'time_frame_field': TimeFrameType.NthDayOfASpecificMonth.value,
                'ordinal': 2,
                'week_day_field': '',
                'month_field': '',
                'first_occurrence': '2024-01-01',
                'auto_create_days': 7,
                'color': '#FD7E14',
                'template': self.template_group.pk,
                'weekend_handling_field': ProblemHandling.Ignore.value,
                'weekend_warning': '',
                'holiday_handling_field': ProblemHandling.Ignore.value,
                'holiday_warning': '',
            },
            initial={'organization': self.organization},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('month_field', form.errors)


class ShiftTemplateFormTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def setUp(self) -> None:
        self.template_group = ShiftTemplateGroup.objects.get(pk=1)
        self.shift_type = ShiftType.objects.get(pk=1)

    def test_valid_template_form_converts_slider_values_to_timedelta(self) -> None:
        form = ShiftTemplateForm(
            self.template_group,
            data={
                'name': 'Late shift',
                'shift_type': self.shift_type.pk,
                'start_delay': 15,
                'duration': 120,
                'required_users': 1,
                'max_users': 2,
                'additional_infos': '',
            },
        )

        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.start_delay, timedelta(minutes=15))
        self.assertEqual(instance.duration, timedelta(minutes=120))

    def test_duration_cannot_exceed_max_shift_length(self) -> None:
        form = ShiftTemplateForm(
            self.template_group,
            data={
                'name': 'Too long shift',
                'shift_type': self.shift_type.pk,
                'start_delay': 15,
                'duration': settings.MAX_SHIFT_LENGTH_MINUTES + 1,
                'required_users': 1,
                'max_users': 2,
                'additional_infos': '',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)


class ParticipantFormTest(TestCase):
    fixtures = ['user', 'organization']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.shift_type = ShiftType.objects.filter(organization=self.organization).first()
        self.shift = Shift.objects.create(
            organization=self.organization,
            shift_type=self.shift_type,
            name='Participant test shift',
            place='K1 Bar',
            start=datetime(2024, 1, 1, 10, 0, 0),
            end=datetime(2024, 1, 1, 12, 0, 0),
            required_users=1,
            max_users=2,
        )
        self.member_user = User.objects.get(username='jd')
        self.target_user = User.objects.get(username='bob')

    def test_add_self_participant_rejects_duplicates(self) -> None:
        participant = Participant.objects.create(user=self.member_user, display_name='')
        self.shift.participants.add(participant)

        form = AddSelfParticipantForm(
            self.shift,
            data={'user': self.member_user.pk, 'display_name': ''},
            initial={'user': self.member_user},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_add_other_participant_accepts_org_member_choice(self) -> None:
        form = AddOtherParticipantForm(
            self.shift,
            data={'org_user': self.member_user.pk, 'other_user': '', 'display_name': ''},
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['user'], self.member_user)

    def test_add_other_participant_rejects_both_user_inputs(self) -> None:
        form = AddOtherParticipantForm(
            self.shift,
            data={
                'org_user': self.member_user.pk,
                'other_user': self.target_user.username,
                'display_name': '',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('org_user', form.errors)
        self.assertIn('other_user', form.errors)
