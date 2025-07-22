from django.core.paginator import Paginator as DjangoPaginator
from django.utils.functional import cached_property

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.pagination import DynamicPageSizeMixin

from ..models import Zaak
from .serializers import ZaakSerializer


class ExactPaginator(DjangoPaginator):
    @cached_property
    def count(self):
        """
        ⚡ restricts values to PK to remove implicit join from SQL query
        """
        return self.object_list.values("pk").count()


class ExactPagination(DynamicPageSizeMixin, PageNumberPagination):
    django_paginator_class = ExactPaginator


class ZaakViewSet(viewsets.ModelViewSet):
    queryset = Zaak.objects.all().order_by("-pk")
    lookup_field = "uuid"
    serializer_class = ZaakSerializer
    pagination_class = ExactPagination
