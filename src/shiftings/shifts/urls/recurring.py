from django.urls import path

from shiftings.shifts.views.recurring import (
    RecurringShiftCreateView, RecurringShiftDetailView, RecurringShiftEditView
)
from shiftings.shifts.views.template import TemplateGroupAddShiftsView

urlpatterns = [
    path('<int:pk>/', RecurringShiftDetailView.as_view(), name='recurring_shift'),
    path('create/<int:org_pk>', RecurringShiftCreateView.as_view(), name='recurring_shift_create'),
    path('<int:pk>/update/', RecurringShiftEditView.as_view(), name='recurring_shift_update'),
]
