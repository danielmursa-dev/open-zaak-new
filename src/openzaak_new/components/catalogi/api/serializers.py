# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact

from rest_framework.serializers import (
    HyperlinkedModelSerializer,
)

from ..models import ZaakType


class ZaakTypeSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ZaakType
        fields = ("identificatie",)
