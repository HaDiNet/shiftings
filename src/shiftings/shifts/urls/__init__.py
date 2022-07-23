from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('shiftings.shifts.urls.shift')),
    path('recurring/', include('shiftings.shifts.urls.recurring_shift'))
]