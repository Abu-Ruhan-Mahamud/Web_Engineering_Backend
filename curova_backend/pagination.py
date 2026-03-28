"""
Reusable pagination helper for function-based views.

DRF's global pagination only works with generic views / viewsets.
Call `paginate_queryset(qs, request)` from any @api_view to get a
properly paginated Response.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def paginate_queryset(queryset, request, serializer_class, context=None):
    """
    Paginate a queryset inside a function-based view.

    Returns a DRF-style paginated Response with `count`, `next`,
    `previous`, and `results` keys.
    """
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = serializer_class(page, many=True, context=context or {})
        return paginator.get_paginated_response(serializer.data)
    # Fallback: unpaginated (shouldn't happen with PageNumberPagination)
    serializer = serializer_class(queryset, many=True, context=context or {})
    from rest_framework.response import Response

    return Response(serializer.data)
