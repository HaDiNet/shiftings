from django.urls import path

from shiftings.shifts.views.attendance import (
    OrganizationAttendanceOverviewView, OrganizationMemberNoteUpdateView
)
from shiftings.shifts.views.summary import OrganizationEditShiftSummarySettingsView, OrganizationShiftSummaryView

urlpatterns = [
    path('organization/<int:pk>/', OrganizationShiftSummaryView.as_view(), name='organization_shift_summary'),
    path('organization/<int:pk>/attendance/', OrganizationAttendanceOverviewView.as_view(),
         name='organization_attendance_overview'),
    path('organization/<int:pk>/member-note/<int:user_pk>/', OrganizationMemberNoteUpdateView.as_view(),
         name='organization_member_note_update'),
    path('organization/<int:pk>/edit', OrganizationEditShiftSummarySettingsView.as_view(),
         name='edit_summary_settings'),
]
