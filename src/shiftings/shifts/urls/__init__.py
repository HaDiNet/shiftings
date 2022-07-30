from django.urls import include, path

urlpatterns = [
    path('', include('shiftings.shifts.urls.shift')),
    path('recurring/', include('shiftings.shifts.urls.recurring_shift')),
    path('type/', include('shiftings.shifts.urls.shift_type'))
]