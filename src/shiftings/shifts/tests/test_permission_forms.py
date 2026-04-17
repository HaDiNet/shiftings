from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from shiftings.organizations.models import Organization
from shiftings.shifts.forms.permission import ParticipationPermissionForm, ParticipationPermissionFormSet
from shiftings.shifts.models import ParticipationPermission, ParticipationPermissionType, Shift, ShiftType


class ParticipationPermissionFormTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.other_organization = Organization.objects.create(name='Other Org')
        self.shift_type = ShiftType.objects.filter(organization=self.organization).first()
        self.shift = Shift.objects.create(
            organization=self.organization,
            shift_type=self.shift_type,
            name='Permission shift',
            place='K1 Bar',
            start=datetime(2024, 1, 3, 10, 0, 0),
            end=datetime(2024, 1, 3, 12, 0, 0),
            required_users=1,
            max_users=2,
        )

    def test_rejects_org_permission_if_all_users_permission_is_more_extensive(self) -> None:
        ParticipationPermission.objects.create_for_instance(
            self.shift,
            organization=None,
            permission_type_field=ParticipationPermissionType.ShiftParticipants,
        )

        form = ParticipationPermissionForm(
            related_object=self.shift,
            data={
                'organization': self.other_organization.pk,
                'permission_type_field': ParticipationPermissionType.Existence,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('permission_type_field', form.errors)


class ParticipationPermissionFormSetTest(TestCase):
    fixtures = ['user', 'organization', 'shift']

    def setUp(self) -> None:
        self.organization = Organization.objects.get(pk=1)
        self.other_organization = Organization.objects.create(name='Formset Org A')
        self.third_organization = Organization.objects.create(name='Formset Org B')
        self.shift_type = ShiftType.objects.filter(organization=self.organization).first()
        self.shift = Shift.objects.create(
            organization=self.organization,
            shift_type=self.shift_type,
            name='Formset shift',
            place='K1 Bar',
            start=datetime(2024, 1, 4, 10, 0, 0),
            end=datetime(2024, 1, 4, 12, 0, 0),
            required_users=1,
            max_users=2,
        )
        content_type = ContentType.objects.get_for_model(self.shift)
        self.permission_one = ParticipationPermission.objects.create(
            referred_content_type=content_type,
            referred_object_id=self.shift.pk,
            organization=self.other_organization,
            permission_type_field=ParticipationPermissionType.Existence,
        )
        self.permission_two = ParticipationPermission.objects.create(
            referred_content_type=content_type,
            referred_object_id=self.shift.pk,
            organization=self.third_organization,
            permission_type_field=ParticipationPermissionType.Participate,
        )

    def test_rejects_duplicate_organization_entries(self) -> None:
        queryset = ParticipationPermission.objects.filter(pk__in=[self.permission_one.pk, self.permission_two.pk])
        formset = ParticipationPermissionFormSet(
            data={
                'form-TOTAL_FORMS': '2',
                'form-INITIAL_FORMS': '2',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-id': str(self.permission_one.pk),
                'form-0-organization': str(self.other_organization.pk),
                'form-0-permission_type_field': str(ParticipationPermissionType.Existence.value),
                'form-1-id': str(self.permission_two.pk),
                'form-1-organization': str(self.other_organization.pk),
                'form-1-permission_type_field': str(ParticipationPermissionType.ShiftDetails.value),
            },
            queryset=queryset,
            form_kwargs={'related_object': self.shift},
        )

        self.assertFalse(formset.is_valid())
        form_errors = [form.errors for form in formset.forms]
        self.assertTrue(any('organization' in errors for errors in form_errors))
