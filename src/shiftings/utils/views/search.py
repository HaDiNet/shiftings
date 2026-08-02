from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet


class SearchableQuerysetMixin:
    search_param_name = 'search_param'
    search_fields: tuple[str, ...] = tuple()

    def get_search_param(self) -> str | None:
        search_param = self.request.GET.get(self.search_param_name)
        if search_param is None:
            return None
        stripped = search_param.strip()
        return stripped or None

    def get_search_fields(self) -> tuple[str, ...]:
        return self.search_fields

    def get_search_query(self, search_param: str) -> Q:
        query = Q()
        for field in self.get_search_fields():
            query |= Q(**{f'{field}__icontains': search_param})
        return query

    def apply_search_filter(self, queryset: QuerySet[Any]) -> QuerySet[Any]:
        search_param = self.get_search_param()
        if search_param is None:
            return queryset
        search_query = self.get_search_query(search_param)
        if search_query == Q():
            return queryset
        return queryset.filter(search_query)
