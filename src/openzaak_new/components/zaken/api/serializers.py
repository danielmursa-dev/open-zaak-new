from rest_framework import serializers
from vng_api_common.serializers import CachedHyperlinkedIdentityField

from ..models import Zaak


class ZaakSerializer(serializers.HyperlinkedModelSerializer):
    url = CachedHyperlinkedIdentityField(view_name="zaak-detail", lookup_field="uuid")

    class Meta:
        model = Zaak
        fields = (
            "url",
            "omschrijving",
            "toelichting",
            "betalingsindicatie",
            "verlenging_reden",
            "opschorting_reden",
            "opschorting_indicatie",
            "opschorting_eerdere_opschorting",
            "archiefnominatie",
            "archiefstatus",
            "processobjectaard",
            "processobject_datumkenmerk",
            "processobject_identificatie",
            "processobject_objecttype",
            "processobject_registratie",
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
        )
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
        }
