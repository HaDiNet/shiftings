from django.urls import path

from shiftings.shifts.views.recurring import (
    RecurringShiftCreateShiftsView, RecurringShiftDetailView, RecurringShiftEditView
)

urlpatterns = [
    path('<int:pk>/', RecurringShiftDetailView.as_view(), name='recurring_shift'),
    path('create/<int:org_pk>', RecurringShiftEditView.as_view(), name='recurring_shift_create'),
    path('<int:pk>/update/', RecurringShiftEditView.as_view(), name='recurring_shift_update'),
    path('<int:pk>/create_shift', RecurringShiftCreateShiftsView.as_view(),
         name='recurring_create_shifts'),
]
