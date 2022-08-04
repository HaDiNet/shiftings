from django.urls import path

from shiftings.mail.views.mail import BaseMailView

urlpatterns = [
    path('', BaseMailView.as_view(), name='mail'),
]
