from django.urls import include, path

from shiftings.shifts.views.permission import ShiftParticipationPermissionEditView
from shiftings.shifts.views.shift import (
    CreateShiftFromTemplateGroup, ShiftDeleteView, ShiftDetailView, ShiftEditView, ShiftOrgSelectView
)

urlpatterns = [
    path('<int:pk>/', ShiftDetailView.as_view(), name='shift'),
    path('create/<int:org_pk>', ShiftEditView.as_view(), name='shift_create'),
    path('create/<int:org_pk>/template', CreateShiftFromTemplateGroup.as_view(), name='shift_create_from_template'),
    path('select_org/', ShiftOrgSelectView.as_view(), name='shift_org_select'),
    path('<int:pk>/update/', ShiftEditView.as_view(), name='shift_update'),
    path('<int:pk>/delete/', ShiftDeleteView.as_view(), name='shift_delete'),
    path('<int:pk>/permissions/', ShiftParticipationPermissionEditView.as_view(), name='shift_part_permissions_edit'),
    path('<int:pk>/participant/', include('shiftings.shifts.urls.participant'))
]
