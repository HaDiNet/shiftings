from django.urls import include, path

urlpatterns = [
    path('', include('shiftings.events.urls.event')),
]