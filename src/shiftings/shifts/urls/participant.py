from django.urls import path

from shiftings.shifts.views.excuse import ExcuseOtherView, ExcuseSelfView, RemoveExcusedView
from shiftings.shifts.views.participant import AddOtherParticipantView, AddSelfParticipantView, RemoveParticipantView

urlpatterns = [
    path('add_me/', AddSelfParticipantView.as_view(), name='add_participant_self'),
    path('add_other/', AddOtherParticipantView.as_view(), name='add_participant_other'),
    path('<int:ppk>/remove/', RemoveParticipantView.as_view(), name='remove_participant'),
    path('excuse_me/', ExcuseSelfView.as_view(), name='excuse_self_from_shift'),
    path('excuse_other/', ExcuseOtherView.as_view(), name='excuse_other_from_shift'),
    path('excused/<int:user_pk>/remove/', RemoveExcusedView.as_view(), name='remove_excused'),
]
