from django.urls import include, path

from shiftings.cal.feed.organization import OrganizationFeed
from shiftings.organizations.views.organization import OrganizationDetailView, OrganizationEditView, \
    OrganizationListView, OwnOrganizationListView

urlpatterns = [
    path('', OrganizationListView.as_view(), name='organizations'),
    path('my/', OwnOrganizationListView.as_view(), name='own_organizations'),
    path('<int:pk>/', OrganizationDetailView.as_view(), name='organization'),
    path('create/', OrganizationEditView.as_view(), name='organization_create'),
    path('<int:pk>/update/', OrganizationEditView.as_view(), name='organization_update'),
    path('<int:pk>/membership/', include('shiftings.organizations.urls.membership')),
    path('<int:pk>/calendar/', OrganizationFeed(), name='organization_calendar'),

    path('<int:pk>/mail/', include('shiftings.mail.urls.organization')),
]
