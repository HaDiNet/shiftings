from typing import Any, List

from django.conf import settings
from django.urls import path
# from django.views.generic import TemplateView
from django.views.generic import TemplateView

from shiftings.accounts.views.auth import UserLoginView, UserLogoutView, UserReLoginView
# from shiftings.accounts.views.user_edit import (PasswordResetConfirmView, PasswordResetView, UserCreateView,
#                                             UserUpdateOtherView, UserUpdateSelfView)
# from shiftings.accounts.views.user_profile import UserProfileView
from shiftings.accounts.views.password import PasswordResetConfirmView, PasswordResetView
from shiftings.accounts.views.user import UserEditView, UserProfileView, UserRegisterView
from shiftings.cal.feed.user import OwnShiftsFeed, UserFeed

urlpatterns: List[Any] = [
    # auth
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # user
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/past/', UserProfileView.as_view(), name='user_profile_past'),
    path('edit/', UserEditView.as_view(), name='user_edit_self'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', TemplateView.as_view(template_name='accounts/password_reset/done.html'),
         name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/success/', TemplateView.as_view(template_name='accounts/password_reset/success.html'),
         name='password_reset_success'),
    path('calendar/', UserFeed(), name='user_calendar'),
    path('participation_calendar/', OwnShiftsFeed(), name='user_participation_calendar'),
]
if settings.FEATURES.get('registration', False):
    urlpatterns.append(path('register/', UserRegisterView.as_view(), name='register'), )

if settings.OAUTH_ENABLED:
    from shiftings.accounts.views.auth import AuthorizeSSOUser

    urlpatterns.append(path('auth/', AuthorizeSSOUser.as_view(), name='auth'), )

if settings.DEBUG:
    urlpatterns.append(path('relogin/', UserReLoginView.as_view(), name='relogin'))
