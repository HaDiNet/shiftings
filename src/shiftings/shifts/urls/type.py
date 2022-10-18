from django.urls import path

from shiftings.shifts.views.type import ShiftTypeEditView

urlpatterns = [
    path('create/<int:org_pk>/', ShiftTypeEditView.as_view(), name='shift_type_create'),
    path('<int:pk>/update/', ShiftTypeEditView.as_view(), name='shift_type_update'),
]
