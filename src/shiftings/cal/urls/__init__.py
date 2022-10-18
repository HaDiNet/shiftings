from django.urls import path

from shiftings.cal.views.day_calendar import DayView
from shiftings.cal.views.month_calendar import MonthCalenderView

urlpatterns = [
    path('overview/day/', DayView.as_view(), name='overview_today'),
    path('overview/day/<theday>/', DayView.as_view(), name='overview_day'),
    # path('overview/week/', DayView.as_view(), name='overview_thisweek'),
    # path('overview/week/<theweek>/', DayView.as_view(), name='overview_week'),
    path('overview/month/', MonthCalenderView.as_view(), name='overview_thismonth'),
    path('overview/month/<themonth>/<theyear>/', MonthCalenderView.as_view(), name='overview_month'),
]
