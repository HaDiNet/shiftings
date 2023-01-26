import json
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from shiftings.organizations.models import Organization
from shiftings.organizations.models.user import OrganizationDummyUser
from shiftings.shifts.models import Participant, Shift, ShiftType


class Command(BaseCommand):
    help = f'Imports shift data into shiftings.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=Path, help='path to json file')
        parser.add_argument('--organization', type=int, help='organization id for which the shifts are imported')

    def handle(self, *args, **options):
        with open(options['path']) as file:
            shifts: list[dict[str, Any]] = json.load(file)
            if not isinstance(shifts, list):
                self.stderr.write('File is not a valid json list.')
                return
        organization = Organization.objects.filter(pk=options['organization']).first()
        if not organization:
            self.stderr.write(f'Organization with id "{options["organization"]}" not found.')
            return
        with transaction.atomic():
            for shift in shifts:
                self.create_shift(organization, shift)

    @staticmethod
    def create_shift(organization: Organization, template: dict[str, Any]) -> None:
        start_date = date.fromisoformat(template['date'])
        start_time = time.fromisoformat(template['start'])
        end_time = time.fromisoformat(template['end'])
        if 'end_date' in template:
            end_date = date.fromisoformat(template['end_date'])
        else:
            end_date = start_date if end_time >= start_time else start_date + timedelta(days=1)

        shift_type = ShiftType.objects.filter(organization=organization, name='System').first()
        if not shift_type:
            shift_type = ShiftType.objects.create(organization=organization, name='System', color='#000080')

        shift = Shift.objects.create(
            name=template['name'],
            organization=organization,
            shift_type=shift_type,
            additional_infos='Created by Shift Import',
            start=datetime.combine(start_date, start_time),
            end=datetime.combine(end_date, end_time),
            locked=True
        )
        for participant in template['participants']:
            user = OrganizationDummyUser.objects.filter(first_name=participant, organization=organization).first()
            if not user:
                user = OrganizationDummyUser.objects.create(first_name=participant, organization=organization,
                                                            username=uuid.uuid4())
            shift.participants.add(Participant.objects.create(user=user))
