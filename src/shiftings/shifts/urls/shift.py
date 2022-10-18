from django.urls import include, path

from shiftings.shifts.views.shift import ShiftDetailView, ShiftEditView

urlpatterns = [
    path('<int:pk>/', ShiftDetailView.as_view(), name='shift'),
    path('create/<int:org_pk>', ShiftEditView.as_view(), name='shift_create'),
    path('<int:pk>/update/', ShiftEditView.as_view(), name='shift_update'),
    path('<int:pk>/participant/', include('shiftings.shifts.urls.participant'))
]
