from django.core.paginator import Paginator as DjangoPaginator
from django.utils.functional import cached_property

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.pagination import DynamicPageSizeMixin

from ..models import Zaak
from .serializers import ZaakSerializer


class CacheQuerysetMixin:
    """
    Mixin for ViewSets to avoid doing redundant calls to `ViewSet.get_queryset()`

    NOTE: make sure that this mixin is applied before any other mixins that override
    `get_queryset`

    `get_queryset` is actually an additional time when pagination is applied to
    an endpoint, similarly it is called an additional time when query parameters are used
    to filter the queryset. To avoid constructing the exact same queryset twice, we cache
    the result on the ViewSet instance which is a different instance for every request,
    so this caching will only be applied for the same request
    """

    _cached_queryset = None

    def get_queryset(self):
        # `get_queryset` is actually executed twice when pagination is applied to
        # an endpoint, to avoid constructing the exact same queryset twice, we cache
        # the result on the ViewSet instance which is a different instance for every request,
        # so this caching will only be applied for the same request
        if self._cached_queryset is None:
            self._cached_queryset = super().get_queryset()
        return self._cached_queryset


class ExactPaginator(DjangoPaginator):
    @cached_property
    def count(self):
        """
        ⚡ restricts values to PK to remove implicit join from SQL query
        """
        return self.object_list.values("pk").count()


class ExactPagination(DynamicPageSizeMixin, PageNumberPagination):
    django_paginator_class = ExactPaginator


class ZaakViewSet(CacheQuerysetMixin, viewsets.ModelViewSet):
    queryset = Zaak.objects.all().order_by("-pk")
    serializer_class = ZaakSerializer
    lookup_field = "uuid"
    pagination_class = ExactPagination
