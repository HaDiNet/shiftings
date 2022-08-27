from django.urls import path

from shiftings.shifts.views.participant import AddSelfParticipantView, RemoveParticipantView, AddOtherParticipantView

urlpatterns = [
    path('add_me/', AddSelfParticipantView.as_view(), name='add_participant_self'),
    path('add_other/', AddOtherParticipantView.as_view(), name='add_participant_other'),
    path('<int:ppk>/remove/', RemoveParticipantView.as_view(), name='remove_participant')
]
