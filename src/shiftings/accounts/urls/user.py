from typing import Any, List

from django.conf import settings
from django.urls import path
# from django.views.generic import TemplateView
from django.views.generic import TemplateView

from shiftings.accounts.views.auth import ShifterLoginView, ShifterLogoutView

# from shiftings.accounts.views.user_edit import (PasswordResetConfirmView, PasswordResetView, UserCreateView,
#                                             UserUpdateOtherView, UserUpdateSelfView)
# from shiftings.accounts.views.user_profile import UserProfileView
from shiftings.accounts.views.password import PasswordResetConfirmView, PasswordResetView
from shiftings.accounts.views.user import ShifterCreateView, ShifterProfileView

urlpatterns: List[Any] = [
    # auth
    path('login/', ShifterLoginView.as_view(), name='login'),
    path('logout/', ShifterLogoutView.as_view(), name='logout'),
    # user
    path('register/', ShifterCreateView.as_view(), name='register'),
    path('profile/', ShifterProfileView.as_view(), name='user_profile'),
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
]
if settings.OAUTH_ENABLED:
    from shiftings.accounts.views.auth import AuthorizeSSOUser

    urlpatterns.append(path('auth/', AuthorizeSSOUser.as_view(), name='auth'), )
