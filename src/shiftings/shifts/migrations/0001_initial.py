# Generated by Django 4.0.9 on 2023-03-23 20:42

import colorfield.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import shiftings.utils.fields.date_time
import shiftings.utils.time.month
import shiftings.utils.time.week


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('events', '0001_initial'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, help_text='Display Name is optional, and will be shown instead of the username', max_length=100, null=True, verbose_name='Display Name')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='accounts.baseuser', verbose_name='User')),
            ],
            options={
                'ordering': ['display_name', 'user'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='RecurringShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('time_frame_field', models.PositiveSmallIntegerField(choices=[(1, 'Nth [weekday] of each month'), (2, 'Nth day of each month'), (3, 'every Nth [weekday]'), (4, 'Nth workday of each month'), (5, 'Nth day of [month]'), (6, 'Nth workday of [month]')], verbose_name='Timeframe Type')),
                ('ordinal', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)])),
                ('week_day_field', shiftings.utils.time.week.WeekDayField(blank=True, choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)], verbose_name='Day of the Week')),
                ('month_field', shiftings.utils.time.month.MonthField(blank=True, choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='Month')),
                ('first_occurrence', shiftings.utils.fields.date_time.DateField(help_text='Choose a minimum day for first occurrence and the system will automatically choose the next applicable day.', verbose_name='First Occurrence')),
                ('weekend_handling_field', models.PositiveSmallIntegerField(choices=[(1, 'ignore'), (2, 'cancel'), (3, 'show warning')], default=1, verbose_name='Weekend problem handling')),
                ('weekend_warning', models.TextField(blank=True, help_text='A maximum of 250 characters is allowed', max_length=250, null=True, verbose_name='Warning text for weekend')),
                ('holiday_handling_field', models.PositiveSmallIntegerField(choices=[(1, 'ignore'), (2, 'cancel'), (3, 'show warning')], default=1, verbose_name='Holidays problem handling')),
                ('holiday_warning', models.TextField(blank=True, help_text='A maximum of 250 characters is allowed', max_length=250, null=True, verbose_name='Warning text for holidays')),
                ('color', colorfield.fields.ColorField(default='#FD7E14', image_field=None, max_length=18, samples=[('#0D6EFD', 'Blue'), ('#6610F2', 'Indigo'), ('#6F42C1', 'Purple'), ('#D63384', 'Pink'), ('#DC3545', 'Red'), ('#FD7E14', 'Orange'), ('#FFC107', 'Yellow'), ('#198754', 'Green'), ('#20C997', 'Teal'), ('#0DCAF0', 'Cyan')])),
                ('manually_disabled', models.BooleanField(default=False, verbose_name='Manually Disabled')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_shifts', to='organizations.organization', verbose_name='Organization')),
            ],
            options={
                'ordering': ['organization', 'name'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ShiftTypeGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_type_groups', to='organizations.organization', verbose_name='Organization')),
            ],
            options={
                'ordering': ['organization', 'order'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ShiftType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('color', colorfield.fields.ColorField(default='#FD7E14', image_field=None, max_length=18, samples=[('#0D6EFD', 'Blue'), ('#6610F2', 'Indigo'), ('#6F42C1', 'Purple'), ('#D63384', 'Pink'), ('#DC3545', 'Red'), ('#FD7E14', 'Orange'), ('#FFC107', 'Yellow'), ('#198754', 'Green'), ('#20C997', 'Teal'), ('#0DCAF0', 'Cyan')])),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shift_types', to='shifts.shifttypegroup', verbose_name='Group')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_types', to='organizations.organization', verbose_name='Organization')),
            ],
            options={
                'ordering': ['group', 'name'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ShiftTemplateGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('place', models.CharField(blank=True, max_length=100, null=True, verbose_name='Place')),
                ('start_time', shiftings.utils.fields.date_time.TimeField(db_index=True, verbose_name='Start Time')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_template_groups', to='organizations.organization', verbose_name='Organization')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ShiftTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('start_delay', models.DurationField(verbose_name='Start Delay')),
                ('duration', models.DurationField(verbose_name='Duration')),
                ('required_users', models.PositiveSmallIntegerField(default=0, help_text='A maximum of 32 users can be required', validators=[django.core.validators.MaxValueValidator(32)], verbose_name='Required User')),
                ('max_users', models.PositiveSmallIntegerField(default=0, help_text='A maximum of 64 users can be present', validators=[django.core.validators.MaxValueValidator(64)], verbose_name='Maximum User')),
                ('additional_infos', models.TextField(blank=True, help_text='A maximum of 1000 characters is allowed', max_length=1000, null=True, verbose_name='Additional Infos')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='shifts.shifttemplategroup', verbose_name='Template Group')),
                ('shift_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shifts.shifttype', verbose_name='Shift Type')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('place', models.CharField(blank=True, max_length=100, null=True, verbose_name='Place')),
                ('required_users', models.PositiveSmallIntegerField(default=0, help_text='A maximum of 32 users can be required', validators=[django.core.validators.MaxValueValidator(32)], verbose_name='Required Users')),
                ('max_users', models.PositiveSmallIntegerField(default=0, help_text='A maximum of 64 users can be present', validators=[django.core.validators.MaxValueValidator(64)], verbose_name='Maximum Users')),
                ('additional_infos', models.TextField(blank=True, help_text='A maximum of 1000 characters is allowed', max_length=1000, null=True, verbose_name='Additional Infos')),
                ('start', shiftings.utils.fields.date_time.DateTimeField(db_index=True, verbose_name='Start Date and Time')),
                ('end', shiftings.utils.fields.date_time.DateTimeField(db_index=True, verbose_name='End Date and Time')),
                ('locked', models.BooleanField(default=False, verbose_name='Locked for Participation')),
                ('warnings', models.TextField(blank=True, help_text='A maximum of 500 characters is allowed', max_length=500, null=True, verbose_name='Warning')),
                ('created', shiftings.utils.fields.date_time.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', shiftings.utils.fields.date_time.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('based_on', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_shifts', to='shifts.recurringshift', verbose_name='Created by Recurring Shift')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='events.event', verbose_name='Event')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='organizations.organization', verbose_name='Organization')),
                ('participants', models.ManyToManyField(blank=True, related_name='shift_set', to='shifts.participant', verbose_name='Users')),
                ('shift_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shifts.shifttype', verbose_name='Shift Type')),
            ],
            options={
                'ordering': ['start', 'end', 'name', 'organization'],
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='recurringshift',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recurring_shifts', to='shifts.shifttemplategroup', verbose_name='Shift Template'),
        ),
        migrations.CreateModel(
            name='OrganizationSummarySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other_shifts_group_name', models.CharField(default='Other', max_length=30, verbose_name='"Other" Shift Type Group Name')),
                ('default_time_range_type', models.PositiveSmallIntegerField(choices=[(1, 'Month'), (2, 'Quarter'), (3, 'Half Year'), (4, 'Year'), (5, 'Decade'), (6, 'Century'), (7, 'Millennium')], default=3, verbose_name='Default time range for summary')),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='summary_settings', to='organizations.organization')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.AddConstraint(
            model_name='shifttypegroup',
            constraint=models.UniqueConstraint(fields=('organization', 'order'), name='shift_type_group_organization_order_unique_constraint'),
        ),
        migrations.AddConstraint(
            model_name='shifttypegroup',
            constraint=models.UniqueConstraint(fields=('organization', 'name'), name='shift_type_group_organization_name_unique_constraint'),
        ),
        migrations.AddConstraint(
            model_name='shifttype',
            constraint=models.UniqueConstraint(fields=('organization', 'name'), name='shift_type_organization_name_unique_constraint'),
        ),
        migrations.AddConstraint(
            model_name='shift',
            constraint=models.CheckConstraint(check=models.Q(('start__lte', django.db.models.expressions.F('end'))), name='shift_start_before_end'),
        ),
    ]
