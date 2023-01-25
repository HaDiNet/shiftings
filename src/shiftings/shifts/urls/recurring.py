from django.urls import path

from shiftings.shifts.views.recurring import (
    RecurringShiftCreateShiftsView, RecurringShiftCreateView, RecurringShiftDetailView, RecurringShiftEditView
)


urlpatterns = [
    path('<int:pk>/', RecurringShiftDetailView.as_view(), name='recurring_shift'),
    path('create/<int:org_pk>', RecurringShiftCreateView.as_view(), name='recurring_shift_create'),
    path('<int:pk>/update/', RecurringShiftEditView.as_view(), name='recurring_shift_update'),
    path('<int:pk>/create_shift', RecurringShiftCreateShiftsView.as_view(),
         name='recurring_create_shifts'),
]
