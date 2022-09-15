from django.urls import include, path

urlpatterns = [
    path('', include('shiftings.shifts.urls.shift')),
    path('recurring/', include('shiftings.shifts.urls.recurring')),
    path('summary/', include('shiftings.shifts.urls.summary')),
    path('template/', include('shiftings.shifts.urls.templates')),
    path('type/', include('shiftings.shifts.urls.type'))
]