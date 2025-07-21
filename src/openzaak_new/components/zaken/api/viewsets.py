from rest_framework import viewsets

from ..models import Zaak
from .serializers import ZaakSerializer


class ZaakViewSet(viewsets.ModelViewSet):
    queryset = Zaak.objects.all()[0:100]
    serializer_class = ZaakSerializer
