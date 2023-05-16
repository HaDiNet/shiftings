from django.urls import path

from shiftings.mail.views.organization import OrganizationMailView
from shiftings.mail.views.participants import ShiftParticipantsMailView

urlpatterns = [
    path('', OrganizationMailView.as_view(), name='organization_mail'),
    path('participants', ShiftParticipantsMailView.as_view(), name='shift_participants_mail'),
]
