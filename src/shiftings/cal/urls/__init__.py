from django.urls import path

from shiftings.cal.feed.token_feeds import (
    TokenEventFeed, TokenOrganizationFeed, TokenOwnShiftsFeed, TokenUserFeed,
)
from shiftings.cal.views.day_calendar import DetailDayView, ShiftTypesDayView
from shiftings.cal.views.month_calendar import MonthCalenderView
from shiftings.cal.views.list import DetailListView, ShiftTypesListView

urlpatterns = [
    path('overview/day/detail/', DetailDayView.as_view(), name='overview_today'),
    path('overview/day/detail/<theday>/', DetailDayView.as_view(), name='overview_day'),
    path('overview/day/shift_types/', ShiftTypesDayView.as_view(), name='overview_today_shift_types'),
    path('overview/day/shift_types/<theday>/', ShiftTypesDayView.as_view(), name='overview_day_shift_types'),
    # path('overview/week/', DayView.as_view(), name='overview_thisweek'),
    # path('overview/week/<theweek>/', DayView.as_view(), name='overview_week'),
    path('overview/month/', MonthCalenderView.as_view(), name='overview_thismonth'),
    path('overview/month/<themonth>/<theyear>/', MonthCalenderView.as_view(), name='overview_month'),
    path('overview/list/detail/', DetailListView.as_view(), name='overview_list'),
    path('overview/list/shift_types/', ShiftTypesListView.as_view(), name='overview_list_shift_types'),
    # Token-based iCal feeds (no session required)
    path('token/<str:token>/user/', TokenUserFeed(), name='token_user_calendar'),
    path('token/<str:token>/participation/', TokenOwnShiftsFeed(), name='token_participation_calendar'),
    path('token/<str:token>/organization/<int:pk>/', TokenOrganizationFeed(), name='token_organization_calendar'),
    path('token/<str:token>/event/<int:pk>/', TokenEventFeed(), name='token_event_calendar'),
]
