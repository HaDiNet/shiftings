from typing import Any

from django.urls import URLPattern, path


def organization_crud_paths(
    *,
    edit_view: Any,
    name_prefix: str,
    delete_view: Any | None = None,
    pk_kwarg: str = 'pk',
    delete_segment: str = 'delete',
    create_pattern: str = 'create/<int:org_pk>/',
    update_pattern: str | None = None,
    delete_pattern: str | None = None,
) -> list[URLPattern]:
    update_pattern = update_pattern or f'<int:{pk_kwarg}>/update/'
    delete_pattern = delete_pattern or f'<int:{pk_kwarg}>/{delete_segment}/'

    urlpatterns = [
        path(create_pattern, edit_view.as_view(), name=f'{name_prefix}_create'),
        path(update_pattern, edit_view.as_view(), name=f'{name_prefix}_update'),
    ]
    if delete_view is not None:
        urlpatterns.append(
            path(
                delete_pattern,
                delete_view.as_view(),
                name=f'{name_prefix}_{delete_segment}',
            )
        )
    return urlpatterns
