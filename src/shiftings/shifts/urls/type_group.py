from django.urls import path

from shiftings.shifts.views.type_group import ShiftTypeGroupDetailView, ShiftTypeGroupEditView, \
    ShiftTypeGroupListView, ShiftTypeGroupRemoveView

urlpatterns = [
    path('<int:org_pk>/', ShiftTypeGroupListView.as_view(), name='shift_type_groups'),
    path('create/<int:org_pk>/', ShiftTypeGroupEditView.as_view(), name='shift_type_group_create'),
    path('<int:pk>/', ShiftTypeGroupDetailView.as_view(), name='shift_type_group_detail'),
    path('<int:pk>/update/', ShiftTypeGroupEditView.as_view(), name='shift_type_group_update'),
    path('<int:pk>/remove/', ShiftTypeGroupRemoveView.as_view(), name='shift_type_group_remove'),
]
