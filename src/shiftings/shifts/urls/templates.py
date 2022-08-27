from django.urls import path

from shiftings.shifts.views.template import TemplateGroupDetailView, TemplateGroupEditView, TemplateGroupListView
from shiftings.shifts.views.type import ShiftTypeEditView, ShiftTypeListView

urlpatterns = [
    path('groups/', TemplateGroupListView.as_view(), name='shift_template_groups'),
    path('groups/<int:pk>/', TemplateGroupDetailView.as_view(), name='shift_template_group'),
    path('groups/create/', TemplateGroupEditView.as_view(), name='shift_template_group_create'),
    path('groups/<int:pk>/update/', TemplateGroupEditView.as_view(), name='shift_template_group_update'),
]
