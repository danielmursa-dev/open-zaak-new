from rest_framework import viewsets

from ..models import Zaak
from .serializers import ZaakSerializer


class ZaakViewSet(viewsets.ModelViewSet):
    queryset = Zaak.objects.all()
    serializer_class = ZaakSerializer
