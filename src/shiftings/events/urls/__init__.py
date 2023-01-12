from django.conf import settings
from django.urls import include, path

urlpatterns = [
]

if settings.FEATURES.get('event', False):
    urlpatterns.append(path('', include('shiftings.events.urls.event')))
