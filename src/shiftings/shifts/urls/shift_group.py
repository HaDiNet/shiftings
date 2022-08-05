from django.urls import path

from shiftings.shifts.views.shift_group import ShiftGroupEditView, ShiftGroupListView

urlpatterns = [
    path('', ShiftGroupListView.as_view(), name='shift_groups'),
    path('create/', ShiftGroupEditView.as_view(), name='shift_group_create'),
    path('<int:pk>/update/', ShiftGroupEditView.as_view(), name='shift_group_update'),
]
