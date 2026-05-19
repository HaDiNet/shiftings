from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin

from shiftings.organizations.models import Membership, MembershipType, Organization, OrganizationDummyUser
from shiftings.utils.admin import RelatedObjectsFilter, register_models


class OrganizationGroupFilter(RelatedObjectsFilter):
	title = 'Organization'
	parameter_name = 'organization'
	related_model = Organization
	related_model_filter = {'members__group__isnull': False}
	queryset_filter_field = 'memberships__organization'
	include_empty_choice = True
	empty_choice_label = 'No organization'
	empty_queryset_filter = {'memberships__isnull': True}


try:
	admin.site.unregister(Group)
except admin.sites.NotRegistered:
	pass


class GroupAdmin(DefaultGroupAdmin):
	def get_list_filter(self, request):
		base = super().get_list_filter(request)
		try:
			# ensure it's a tuple before appending
			return tuple(list(base) + [OrganizationGroupFilter])
		except Exception:
			return (OrganizationGroupFilter,)


admin.site.register(Group, GroupAdmin)


register_models(Organization,)

register_models(
	Membership,
	MembershipType,
	OrganizationDummyUser,
)
