from django.urls import path

from shiftings.shifts.views.shift_type import ShiftTypeEditView, ShiftTypeListView

urlpatterns = [
    path('', ShiftTypeListView.as_view(), name='shift_types'),
    path('create/', ShiftTypeEditView.as_view(), name='shift_type_create'),
    path('<int:pk>/update/', ShiftTypeEditView.as_view(), name='shift_type_update'),
]
