from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from shiftings.cal.views.month_calendar import OrganizationMonthView

urlpatterns = [
    path('month/<model_name>/<int:model_id>', OrganizationMonthView.as_view(), name='month_calendar'),
]
