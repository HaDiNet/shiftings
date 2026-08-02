from django.urls import include, path

from shiftings.shifts.views.permission import ShiftParticipationPermissionEditView
from shiftings.shifts.views.shift import (
    CreateShiftFromTemplateGroup, ShiftDeleteView, ShiftDetailView, ShiftEditView, ShiftOrgSelectView
)
from shiftings.utils.url_patterns import organization_crud_paths

urlpatterns = [
    path('<int:pk>/', ShiftDetailView.as_view(), name='shift'),
    path('create/<int:org_pk>/template', CreateShiftFromTemplateGroup.as_view(), name='shift_create_from_template'),
    path('select_org/', ShiftOrgSelectView.as_view(), name='shift_org_select'),
    path('<int:pk>/permissions/', ShiftParticipationPermissionEditView.as_view(), name='shift_part_permissions_edit'),
    path('<int:pk>/participant/', include('shiftings.shifts.urls.participant'))
] + organization_crud_paths(
    edit_view=ShiftEditView,
    delete_view=ShiftDeleteView,
    name_prefix='shift',
    create_pattern='create/<int:org_pk>',
)
