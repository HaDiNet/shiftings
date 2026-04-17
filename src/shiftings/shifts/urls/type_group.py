from django.urls import path

from shiftings.shifts.views.type_group import (
    ShiftTypeGroupDetailView, ShiftTypeGroupEditView, ShiftTypeGroupListView, ShiftTypeGroupMoveDownView,
    ShiftTypeGroupMoveUpView, ShiftTypeGroupRemoveView
)
from shiftings.utils.url_patterns import organization_crud_paths

urlpatterns = [
    path('<int:org_pk>/', ShiftTypeGroupListView.as_view(), name='shift_type_groups'),
    path('detail/<int:pk>/', ShiftTypeGroupDetailView.as_view(), name='shift_type_group_detail'),
    path('<int:pk>/move_up/', ShiftTypeGroupMoveUpView.as_view(), name='shift_type_group_move_up'),
    path('<int:pk>/move_down/', ShiftTypeGroupMoveDownView.as_view(), name='shift_type_group_move_down'),
] + organization_crud_paths(
    edit_view=ShiftTypeGroupEditView,
    delete_view=ShiftTypeGroupRemoveView,
    name_prefix='shift_type_group',
    delete_segment='remove',
)
