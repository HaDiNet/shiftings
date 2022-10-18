from django.urls import path

from shiftings.shifts.views.template import (
    ShiftTemplateGroupDeleteView, ShiftTemplateGroupDetailView, ShiftTemplateGroupEditView
)

urlpatterns = [
    path('<int:pk>/', ShiftTemplateGroupDetailView.as_view(), name='shift_template_group'),
    path('create/<int:org_pk>/', ShiftTemplateGroupEditView.as_view(), name='shift_template_group_create'),
    path('<int:pk>/update/', ShiftTemplateGroupEditView.as_view(), name='shift_template_group_update'),
    path('<int:pk>/delete/', ShiftTemplateGroupDeleteView.as_view(), name='shift_template_group_delete'),
]
