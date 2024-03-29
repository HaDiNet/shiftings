# Generated by Django 4.0.9 on 2023-04-05 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='confirm_participation_active',
            field=models.BooleanField(default=False, help_text='Whether the participants can be confirmed or not. Default: False', verbose_name='Confirm Participants'),
        ),
    ]
