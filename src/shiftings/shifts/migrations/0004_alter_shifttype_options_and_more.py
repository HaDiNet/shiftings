# Generated by Django 4.0.6 on 2022-10-20 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_alter_membershiptype_options'),
        ('shifts', '0003_alter_organizationsummarysettings_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shifttype',
            options={'default_permissions': (), 'ordering': ['name']},
        ),
        migrations.RemoveConstraint(
            model_name='shifttype',
            name='shift_type_organization_position_unique_constraint',
        ),
        migrations.RemoveConstraint(
            model_name='shifttype',
            name='shift_type_event_position_unique_constraint',
        ),
        migrations.RemoveConstraint(
            model_name='shifttype',
            name='shift_type_event_name_unique_constraint',
        ),
        migrations.RemoveConstraint(
            model_name='shifttype',
            name='shift_type_name_or_organization',
        ),
        migrations.RemoveField(
            model_name='shifttype',
            name='event',
        ),
        migrations.RemoveField(
            model_name='shifttype',
            name='position',
        ),
        migrations.AlterField(
            model_name='shifttype',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='shifttype',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_types', to='organizations.organization', verbose_name='Organization'),
        ),
    ]