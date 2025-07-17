from rest_framework import viewsets

from ..models import Zaak
from .serializers import ZaakSerializer


class ZaakViewSet(viewsets.ModelViewSet):
    queryset = Zaak.objects.all()  # .order_by("-pk")
    serializer_class = ZaakSerializer
