from django.urls import path

from shiftings.shifts.views.summary import OrganizationEditShiftSummarySettingsView, OrganizationShiftSummaryView

urlpatterns = [
    path('organization/<int:pk>/', OrganizationShiftSummaryView.as_view(), name='organization_shift_summary'),
    path('organization/<int:pk>/edit', OrganizationEditShiftSummarySettingsView.as_view(),
         name='edit_summary_settings'),
]
