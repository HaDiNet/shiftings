from django.urls import path

from shiftings.mail.views.organization import OrganizationMailView

urlpatterns = [
    path('', OrganizationMailView.as_view(), name='organization_mail'),
]
