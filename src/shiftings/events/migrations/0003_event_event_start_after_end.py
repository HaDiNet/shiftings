# Generated by Django 4.0.6 on 2022-08-04 17:31

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='event',
            constraint=models.CheckConstraint(check=models.Q(('start_date__lte', django.db.models.expressions.F('end_date'))), name='event_start_after_end'),
        ),
    ]