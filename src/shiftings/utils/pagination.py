from __future__ import annotations

from typing import Any, Collection, Dict, Optional, Tuple, TYPE_CHECKING, TypeVar, Union

from django.core.paginator import InvalidPage, Page, Paginator
from django.db.models import Model
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.db.models import QuerySet

T = TypeVar('T', bound=Model)


def paginate_iterable(request: HttpRequest, iterable: Union[Collection, QuerySet],
                      page_size: int, page_parameter: str = 'page') -> Tuple[Optional[Paginator], Optional[Page]]:
    paginator = Paginator(iterable, page_size)
    # noinspection PyArgumentList
    page = request.GET.get(page_parameter) or 1
    try:
        page_number = int(page)
    except ValueError:
        if page == 'last':
            page_number = paginator.num_pages
        else:
            page_number = 1
    try:
        return paginator, paginator.page(page_number)
    except InvalidPage:
        return None, None


def get_pagination_context(request: HttpRequest, iterable: Union[Collection, QuerySet], paginate_by: int,
                           page_name: str, prefix: str = '') -> Dict[str, Any]:
    if prefix:
        prefix += '_'

    paginator, page = paginate_iterable(request, iterable, paginate_by, page_name)
    if paginator is not None and page is not None:
        return {
            f'{prefix}page_obj': page,
            f'{prefix}is_paginated': page.has_other_pages(),
            f'{prefix}page_name': page_name,
            f'{prefix}object_list': page.object_list
        }
    else:
        return {
            f'{prefix}page_obj': None,
            f'{prefix}paginated': False,
            f'{prefix}page_name': None,
            f'{prefix}object_list': iterable
        }
