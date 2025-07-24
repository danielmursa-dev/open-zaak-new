from rest_framework import serializers
from vng_api_common.serializers import (
    CachedHyperlinkedIdentityField,
    CachedHyperlinkedRelatedField,
    GegevensGroepSerializer,
)

from ..models import Zaak


class ProcessobjectSerializer(GegevensGroepSerializer):
    class Meta:
        model = Zaak
        gegevensgroep = "processobject"


class OpschortingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Zaak
        gegevensgroep = "opschorting"
        extra_kwargs = {
            "indicatie": {"label": "Indicatie"},
            "eerdere_opschorting": {
                "label": "Eerdere opschorting",
                "read_only": True,
            },
            "reden": {"label": "Reden", "allow_blank": True},
        }


class VerlengingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Zaak
        gegevensgroep = "verlenging"
        extra_kwargs = {"reden": {"label": "Reden"}, "duur": {"label": "Duur"}}

    def to_representation(self, instance):
        if not instance["duur"]:
            return None
        return super().to_representation(instance)


class ZaakSerializer(serializers.HyperlinkedModelSerializer):
    url = CachedHyperlinkedIdentityField(view_name="zaak-detail", lookup_field="uuid")
    processobject = ProcessobjectSerializer(
        required=False,
        allow_null=True,
    )
    opschorting = OpschortingSerializer(
        required=False,
        allow_null=True,
    )
    verlenging = VerlengingSerializer(
        required=False,
        allow_null=True,
    )
    deelzaken = CachedHyperlinkedRelatedField(
        read_only=True,
        many=True,
        view_name="zaak-detail",
        lookup_url_kwarg="uuid",
        lookup_field="uuid",
    )

    class Meta:
        model = Zaak
        fields = (
            "url",
            "omschrijving",
            "toelichting",
            "betalingsindicatie",
            "opschorting",
            "archiefnominatie",
            "archiefstatus",
            "processobjectaard",
            "processobject",
            "communicatiekanaal_naam",
            "registratiedatum",
            "startdatum",
            "einddatum",
            "einddatum_gepland",
            "uiterlijke_einddatum_afdoening",
            "publicatiedatum",
            "laatste_betaaldatum",
            "archiefactiedatum",
            "startdatum_bewaartermijn",
            "created_on",
            "verantwoordelijke_organisatie",
            "opdrachtgevende_organisatie",
            "zaakgeometrie",
            "verlenging",
            "vertrouwelijkheidaanduiding",
            "selectielijstklasse",
            "communicatiekanaal",
            "producten_of_diensten",
            "hoofdzaak",
            "deelzaken",
            "_zaaktype",
        )
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "hoofdzaak": {
                "lookup_field": "uuid",
                "queryset": Zaak.objects.all(),
            },
            "_zaaktype": {
                "lookup_field": "uuid",
                "max_length": 1000,
                "min_length": 1,
            },
        }
