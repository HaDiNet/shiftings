from django.urls import path

from shiftings.shifts.views.template import (
    ShiftTemplateGroupDeleteView, ShiftTemplateGroupDetailView, ShiftTemplateGroupEditView, ShiftTemplateGroupListView
)

urlpatterns = [
    path('', ShiftTemplateGroupListView.as_view(), name='shift_template_groups'),
    path('create/', ShiftTemplateGroupEditView.as_view(), name='shift_template_group_create'),
    path('<int:pk>/', ShiftTemplateGroupDetailView.as_view(), name='shift_template_group'),
    path('<int:pk>/update/', ShiftTemplateGroupEditView.as_view(), name='shift_template_group_update'),
    path('<int:pk>/delete/', ShiftTemplateGroupDeleteView.as_view(), name='shift_template_group_delete'),
]
