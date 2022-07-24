from django.urls import path

from shiftings.organizations.views.membership import MembershipAddHelperView, MembershipAddManagerView, \
    MembershipAddMemberView, MembershipRemoveView

urlpatterns = [
    path('add_manager/', MembershipAddManagerView.as_view(), name='membership_add_manager'),
    path('add_member/', MembershipAddMemberView.as_view(), name='membership_add_member'),
    path('add_helper/', MembershipAddHelperView.as_view(), name='membership_add_helper'),
    path('remove/<int:mpk>/', MembershipRemoveView.as_view(), name='membership_remove')
]
