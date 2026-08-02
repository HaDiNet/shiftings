from django.urls import path

from shiftings.shifts.views.template import (
    ShiftTemplateGroupDeleteView, ShiftTemplateGroupDetailView, ShiftTemplateGroupEditView, TemplateGroupAddShiftsView,
    TemplateGroupParticipationPermissionEditView
)
from shiftings.utils.url_patterns import organization_crud_paths

urlpatterns = [
    path('<int:pk>/', ShiftTemplateGroupDetailView.as_view(), name='shift_template_group'),
    path('<int:pk>/templates/', TemplateGroupAddShiftsView.as_view(), name='template_group_update_shifts'),
    path('<int:pk>/permissions/', TemplateGroupParticipationPermissionEditView.as_view(),
         name='template_group_update_permissions'),
] + organization_crud_paths(
    edit_view=ShiftTemplateGroupEditView,
    delete_view=ShiftTemplateGroupDeleteView,
    name_prefix='shift_template_group',
)
