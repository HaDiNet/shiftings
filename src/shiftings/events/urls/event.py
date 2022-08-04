from django.urls import path

from shiftings.cal.feed.event import EventFeed, PublicEventsFeed
from shiftings.events.views.event import EventDetailView, EventEditView, EventListView, FutureEventListView

urlpatterns = [
    path('', EventListView.as_view(), name='events'),
    path('calendar/', PublicEventsFeed(), name='public_events_calendar'),
    path('next/', FutureEventListView.as_view(), name='next_events'),
    path('<int:pk>/', EventDetailView.as_view(), name='event'),
    path('create/', EventEditView.as_view(), name='event_create'),
    path('<int:pk>/update/', EventEditView.as_view(), name='event_update'),
    path('<int:pk>/calendar/', EventFeed(), name='event_calendar'),
]
