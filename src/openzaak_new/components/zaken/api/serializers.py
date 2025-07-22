from rest_framework import serializers

from ..models import Zaak


class ZaakSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(
        view_name="zaak-detail",
        lookup_field="uuid",
        read_only=True,
    )

    class Meta:
        model = Zaak
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "uuid": {"read_only": True},
        }
        fields = (
            "url",
            "omschrijving",
        )
