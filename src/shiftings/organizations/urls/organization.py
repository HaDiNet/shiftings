from django.urls import include, path

from shiftings.cal.feed.organization import OrganizationFeed
from shiftings.organizations.views.organization import (
    OrganizationAdminView, OrganizationEditView, OrganizationListView, OrganizationSettingsView, OrganizationShiftsView,
    OwnOrganizationListView
)

urlpatterns = [
    # admin only
    path('', OrganizationListView.as_view(), name='organizations'),
    path('create/', OrganizationEditView.as_view(), name='organization_create'),
    # members
    path('my/', OwnOrganizationListView.as_view(), name='own_organizations'),
    path('<int:pk>/', OrganizationShiftsView.as_view(), name='organization'),
    path('<int:pk>/admin/', OrganizationAdminView.as_view(), name='organization_admin'),
    path('<int:pk>/settings/', OrganizationSettingsView.as_view(), name='organization_settings'),
    path('<int:pk>/update/', OrganizationEditView.as_view(), name='organization_update'),
    # feed
    path('<int:pk>/calendar/', OrganizationFeed(), name='organization_calendar'),

    # includes
    path('<int:org_pk>/claim_users/', include('shiftings.organizations.urls.user')),
    path('<int:org_pk>/membership/', include('shiftings.organizations.urls.membership')),
    path('<int:org_pk>/mail/', include('shiftings.mail.urls.organization')),
]
