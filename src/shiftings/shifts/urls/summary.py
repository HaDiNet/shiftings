from django.urls import path

from shiftings.shifts.views.summary import OrganizationShiftSummaryView

urlpatterns = [
    path('organization/<int:pk>/', OrganizationShiftSummaryView.as_view(), name='organization_shift_summary'),
]
