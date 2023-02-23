from django.urls import include, path

urlpatterns = [
    path('', include('shiftings.organizations.urls.organization')),
]
