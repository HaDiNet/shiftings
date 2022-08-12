from django.urls import path

from shiftings.organizations.views.membership import MembershipAddMemberView, MembershipRemoveView
from shiftings.organizations.views.membership_type import MembershipTypeEditView, MembershipTypeRemoveView

urlpatterns = [
    path('add_member/', MembershipAddMemberView.as_view(), name='membership_add_member'),
    path('remove/<int:mpk>/', MembershipRemoveView.as_view(), name='membership_remove'),
    path('add_type/', MembershipTypeEditView.as_view(), name='membership_type_add'),
    path('edit_type/<int:mpk>/', MembershipTypeEditView.as_view(), name='membership_type_edit'),
    path('remove_type/<int:mpk>/', MembershipTypeRemoveView.as_view(), name='membership_type_remove')
]
