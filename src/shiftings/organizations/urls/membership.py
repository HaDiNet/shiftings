from django.urls import path

from shiftings.organizations.views.membership import MembershipAddMemberView, MembershipRemoveView

urlpatterns = [
    path('add_member/', MembershipAddMemberView.as_view(), name='membership_add_member'),
    path('remove/<int:mpk>/', MembershipRemoveView.as_view(), name='membership_remove')
]
