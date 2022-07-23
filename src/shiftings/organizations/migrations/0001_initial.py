# Generated by Django 4.0.6 on 2022-07-23 15:15

from django.db import migrations, models
import phonenumber_field.modelfields
import shiftings.organizations.models.organization


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_membership'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('logo', models.ImageField(blank=True, null=True, upload_to=shiftings.organizations.models.organization.logo_upload_path, verbose_name='Logo')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-Mail')),
                ('telephone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Telephone Number')),
                ('website', models.URLField(blank=True, null=True, verbose_name='Website')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('helpers', models.ManyToManyField(related_name='organizations_helper', to='accounts.membership', verbose_name='Helpers')),
                ('managers', models.ManyToManyField(related_name='managed_organizations', to='accounts.membership', verbose_name='Manager')),
                ('members', models.ManyToManyField(related_name='organization_memberships', to='accounts.membership', verbose_name='Members')),
            ],
        ),
    ]
