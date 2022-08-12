from django.urls import include, path

urlpatterns = [
    path('', include('shiftings.shifts.urls.shift')),
    path('recurring/', include('shiftings.shifts.urls.recurring')),
    path('type/', include('shiftings.shifts.urls.type')),
    path('summary/', include('shiftings.shifts.urls.summary'))
]