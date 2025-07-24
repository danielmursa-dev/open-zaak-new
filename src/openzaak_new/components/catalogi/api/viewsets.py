# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
from rest_framework import viewsets

from ..models import ZaakType
from .serializers import ZaakTypeSerializer


class ZaakTypeViewSet(viewsets.ModelViewSet):
    queryset = ZaakType.objects.all()
    serializer_class = ZaakTypeSerializer
    lookup_field = "uuid"
