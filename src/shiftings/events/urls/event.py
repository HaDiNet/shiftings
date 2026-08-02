from django.urls import path

from shiftings.cal.feed.event import EventFeed, PublicEventsFeed
from shiftings.events.views.event import EventDetailView, EventEditView, EventListView, FutureEventsListView, \
    MyEventsListView, MyFutureEventsListView
from shiftings.utils.url_patterns import organization_crud_paths

urlpatterns = [
    path('', EventListView.as_view(), name='events'),
    path('upcoming/', FutureEventsListView.as_view(), name='future_events'),
    path('my/', MyEventsListView.as_view(), name='my_events'),
    path('my_upcoming/', MyFutureEventsListView.as_view(), name='my_future_events'),
    path('calendar/', PublicEventsFeed(), name='public_events_calendar'),
    path('<int:pk>/', EventDetailView.as_view(), name='event'),
    path('<int:pk>/calendar/', EventFeed(), name='event_calendar'),
] + organization_crud_paths(
    edit_view=EventEditView,
    name_prefix='event',
)
