from django.urls import path

from shiftings.shifts.views.type_group import ShiftTypeGroupListView

urlpatterns = [
    path('<int:org_pk>/', ShiftTypeGroupListView.as_view(), name='shift_type_groups'),
]
