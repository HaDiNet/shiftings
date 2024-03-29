# Generated by Django 4.0.9 on 2023-12-21 20:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_organization_confirm_participation_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membershiptype',
            options={'default_permissions': (), 'ordering': ['organization', '-admin', '-default', 'name'], 'permissions': [('edit_organization', 'edit organization details'), ('see_members', 'see members of the organization'), ('see_statistics', 'see shift participation statistics'), ('send_mail', 'send emails to everyone in the organization'), ('edit_membership_types', 'create and update membership types for the organization'), ('edit_members', 'add and remove members for the organization'), ('edit_events', 'create and update events for the organization'), ('edit_recurring_shifts', 'create and update recurring shifts for the organization'), ('edit_shift_templates', 'create and update shifts templates for the organization'), ('edit_shifts', 'create and update shifts for the organization'), ('delete_shifts', 'delete uncompleted shifts for the organization'), ('remove_others_from_shifts', 'remove others from shifts'), ('add_non_members_to_shifts', 'add other users that are not members of the organization to shifts'), ('add_members_to_shifts', 'add other organization members to shifts'), ('participate_in_shift', 'participate in shifts'), ('add_to_past_shift', 'add self/others (depending on other permissions) to past shifts')]},
        ),
    ]
