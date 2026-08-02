from django.urls import path

from shiftings.shifts.views.recurring import (
    RecurringShiftCreateShiftsView, RecurringShiftDeleteView, RecurringShiftDetailView, RecurringShiftEditView
)
from shiftings.utils.url_patterns import organization_crud_paths



urlpatterns = [
    path('<int:pk>/', RecurringShiftDetailView.as_view(), name='recurring_shift'),
    path('<int:pk>/create_shift', RecurringShiftCreateShiftsView.as_view(),
         name='recurring_create_shifts'),
] + organization_crud_paths(
    edit_view=RecurringShiftEditView,
    delete_view=RecurringShiftDeleteView,
    name_prefix='recurring_shift',
)
