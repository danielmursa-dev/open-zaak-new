from rest_framework import serializers
from vng_api_common.serializers import CachedHyperlinkedIdentityField

from ..models import Zaak


class ZaakSerializer(serializers.HyperlinkedModelSerializer):
    url = CachedHyperlinkedIdentityField(view_name="zaak-detail", lookup_field="uuid")

    class Meta:
        model = Zaak
        fields = ("url", "omschrijving")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
        }
