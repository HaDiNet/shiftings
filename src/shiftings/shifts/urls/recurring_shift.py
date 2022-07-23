from django.urls import path

from shiftings.shifts.views.recurring_shift import RecurringShiftDetailView, RecurringShiftEditView, \
    RecurringShiftListView
from shiftings.shifts.views.shift import ShiftDetailView

urlpatterns = [
    path('', RecurringShiftListView.as_view(), name='recurring_shifts'),
    path('<int:pk>/', RecurringShiftDetailView.as_view(), name='recurring_shift'),
    path('create/', RecurringShiftEditView.as_view(), name='recurring_shift_create'),
    path('<int:pk>/update/', RecurringShiftEditView.as_view(), name='recurring_shift_update'),
]