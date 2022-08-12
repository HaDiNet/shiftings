from django.urls import path

from shiftings.shifts.views.recurring import (
    RecurringShiftCreateView, RecurringShiftDetailView, RecurringShiftEditView, RecurringShiftListView
)
from shiftings.shifts.views.template import TemplateGroupAddShiftsView

urlpatterns = [
    path('', RecurringShiftListView.as_view(), name='recurring_shifts'),
    path('<int:pk>/', RecurringShiftDetailView.as_view(), name='recurring_shift'),
    path('create/', RecurringShiftCreateView.as_view(), name='recurring_shift_create'),
    path('<int:pk>/update/', RecurringShiftEditView.as_view(), name='recurring_shift_update'),
    path('<int:pk>/template/', TemplateGroupAddShiftsView.as_view(), name='recurring_shift_template'),
]
