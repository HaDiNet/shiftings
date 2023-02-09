from django.urls import path

from shiftings.organizations.views.user import ClaimUserListView, ClaimUserView, UnclaimUserView

urlpatterns = [
    path('', ClaimUserListView.as_view(), name='claim_user_list'),
    path('<int:pk>/claim/', ClaimUserView.as_view(), name='claim_user'),
    path('<int:pk>/unclaim/', UnclaimUserView.as_view(), name='unclaim_user'),
]
