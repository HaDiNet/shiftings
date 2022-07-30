from django.urls import include, path

from shiftings.shifts.views.shift import FutureShiftListView, ShiftDetailView, ShiftEditView, ShiftListView

urlpatterns = [
    path('', ShiftListView.as_view(), name='shifts'),
    path('next/', FutureShiftListView.as_view(), name='next_shifts'),
    path('<int:pk>/', ShiftDetailView.as_view(), name='shift'),
    path('create/', ShiftEditView.as_view(), name='shift_create'),
    path('<int:pk>/update/', ShiftEditView.as_view(), name='shift_update'),
    path('<int:pk>/participant/', include('shiftings.shifts.urls.participant'))
]
