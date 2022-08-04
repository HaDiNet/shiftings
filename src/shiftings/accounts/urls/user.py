from typing import Any, List

from django.conf import settings
from django.urls import path
# from django.views.generic import TemplateView
from django.views.generic import TemplateView

from shiftings.accounts.views.auth import UserLoginView, UserLogoutView

# from shiftings.accounts.views.user_edit import (PasswordResetConfirmView, PasswordResetView, UserCreateView,
#                                             UserUpdateOtherView, UserUpdateSelfView)
# from shiftings.accounts.views.user_profile import UserProfileView
from shiftings.accounts.views.password import PasswordResetConfirmView, PasswordResetView
from shiftings.accounts.views.user import UserRegisterView, UserProfileView, UserEditView
from shiftings.cal.feed.user import OwnShiftsFeed, UserFeed

urlpatterns: List[Any] = [
    # auth
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # user
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('self/edit/', UserEditView.as_view(), name='user_edit_self'),
    # path('<int:pk>/', UserProfileView.as_view(), name='user_detail'),
    # path('create/', UserCreateView.as_view(), name='user_create'),
    # path('<int:pk>/update/', UserUpdateOtherView.as_view(), name='user_update'),
    # path('update/', UserUpdateSelfView.as_view(), name='user_update_self'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', TemplateView.as_view(template_name='accounts/password_reset/done.html'),
         name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/success/', TemplateView.as_view(template_name='accounts/password_reset/success.html'),
         name='password_reset_success'),
    path('<int:pk>/calendar/', UserFeed(), name='user_calendar'),
    path('<int:pk>/participation_calendar/', OwnShiftsFeed(), name='user_participation_calendar'),
]
if settings.OAUTH_ENABLED:
    from shiftings.accounts.views.auth import AuthorizeSSOUser

    urlpatterns.append(path('auth/', AuthorizeSSOUser.as_view(), name='auth'), )
