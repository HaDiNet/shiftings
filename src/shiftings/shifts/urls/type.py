from django.urls import path

from shiftings.shifts.views.type import ShiftTypeDeleteView, ShiftTypeEditView

urlpatterns = [
    path('create/<int:org_pk>/', ShiftTypeEditView.as_view(), name='shift_type_create'),
    path('<int:pk>/update/', ShiftTypeEditView.as_view(), name='shift_type_update'),
    path('<int:pk>/delete/', ShiftTypeDeleteView.as_view(), name='shift_type_delete'),
]
