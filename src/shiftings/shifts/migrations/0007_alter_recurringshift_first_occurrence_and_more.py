# Generated by Django 4.0.9 on 2023-02-23 22:03

from django.db import migrations, models
import django.db.models.deletion
import shiftings.utils.fields.date_time


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0006_alter_recurringshift_holiday_warning_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringshift',
            name='first_occurrence',
            field=shiftings.utils.fields.date_time.DateField(help_text='Choose a minimum day for first occurrence and the system will automatically choose the next applicable day.', verbose_name='First Occurrence'),
        ),
        migrations.AlterField(
            model_name='recurringshift',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recurring_shifts', to='shifts.shifttemplategroup', verbose_name='Shift Template'),
        ),
    ]
