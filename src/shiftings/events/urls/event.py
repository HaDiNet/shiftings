from django.urls import path

from shiftings.events.views.event import EventDetailView, EventEditView, EventListView, FutureEventListView

urlpatterns = [
    path('', EventListView.as_view(), name='events'),
    path('next/', FutureEventListView.as_view(), name='next_events'),
    path('<int:pk>/', EventDetailView.as_view(), name='event'),
    path('create/', EventEditView.as_view(), name='event_create'),
    path('<int:pk>/update/', EventEditView.as_view(), name='event_update'),
]
