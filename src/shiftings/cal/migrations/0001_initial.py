from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hide_public_shifts', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='calendar_filter',
                                              to=settings.AUTH_USER_MODEL)),
                ('hidden_public_organizations', models.ManyToManyField(blank=True,
                                                                       related_name='hidden_calendar_filters',
                                                                       to='organizations.organization')),
            ],
            options={
                'default_permissions': (),
            },
        ),
    ]
