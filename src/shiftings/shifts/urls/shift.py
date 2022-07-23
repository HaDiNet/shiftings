from django.urls import path

from shiftings.shifts.views.shift import ShiftEditView, ShiftDetailView, ShiftListView

urlpatterns = [
    path('', ShiftListView.as_view(), name='shifts'),
    path('<int:pk>/', ShiftDetailView.as_view(), name='shift'),
    path('create/', ShiftEditView.as_view(), name='shift_create'),
    path('<int:pk>/update/', ShiftEditView.as_view(), name='shift_update'),
]
