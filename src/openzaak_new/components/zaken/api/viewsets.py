from rest_framework import viewsets
from rest_framework.pagination import CursorPagination

from ..models import Zaak
from .serializers import ZaakSerializer


class ZaakCursorPagination(CursorPagination):
    page_size = 100
    ordering = "-id"


class ZaakViewSet(viewsets.ModelViewSet):
    queryset = Zaak.objects.all()
    serializer_class = ZaakSerializer
    pagination_class = ZaakCursorPagination
