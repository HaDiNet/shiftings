from django.urls import path

from shiftings.organizations.views.membership import MembershipAddView, MembershipRemoveView
from shiftings.organizations.views.membership_type import MembershipTypeEditView, MembershipTypeRemoveView

urlpatterns = [
    # membership types
    path('add_type/', MembershipTypeEditView.as_view(), name='membership_type_add'),
    path('edit_type/<int:member_pk>/', MembershipTypeEditView.as_view(), name='membership_type_edit'),
    path('remove_type/<int:member_pk>/', MembershipTypeRemoveView.as_view(), name='membership_type_remove'),
    # members
    path('add_member/', MembershipAddView.as_view(), name='membership_add_member'),
    path('remove/<int:member_pk>/', MembershipRemoveView.as_view(), name='membership_remove')
]
