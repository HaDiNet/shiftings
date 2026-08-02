from shiftings.shifts.views.type import ShiftTypeDeleteView, ShiftTypeEditView
from shiftings.utils.url_patterns import organization_crud_paths

urlpatterns = organization_crud_paths(
    edit_view=ShiftTypeEditView,
    delete_view=ShiftTypeDeleteView,
    name_prefix='shift_type',
)
