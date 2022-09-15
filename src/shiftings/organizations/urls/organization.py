from django.urls import include, path

from shiftings.cal.feed.organization import OrganizationFeed
from shiftings.organizations.views.organization import OrganizationAdminView, OrganizationEditView, \
    OrganizationListView, OwnOrganizationListView, OrganizationShiftsView

urlpatterns = [
    # admin only
    path('', OrganizationListView.as_view(), name='organizations'),
    path('create/', OrganizationEditView.as_view(), name='organization_create'),
    # members
    path('my/', OwnOrganizationListView.as_view(), name='own_organizations'),
    path('<int:org_pk>/', OrganizationShiftsView.as_view(), name='organization'),
    path('<int:org_pk>/admin/', OrganizationAdminView.as_view(), name='organization_admin'),
    path('<int:org_pk>/update/', OrganizationEditView.as_view(), name='organization_update'),
    # feed
    path('<int:org_pk>/calendar/', OrganizationFeed(), name='organization_calendar'),

    # includes
    path('<int:org_pk>/membership/', include('shiftings.organizations.urls.membership')),
    path('<int:org_pk>/mail/', include('shiftings.mail.urls.organization')),
]
