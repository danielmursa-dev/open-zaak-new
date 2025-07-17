from rest_framework import serializers
from ..models import Zaak


class ZaakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zaak
        fields = ["id"]
