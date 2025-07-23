import datetime
import uuid

from django.contrib.gis.db.models import GeometryField
from django.db import models
from django.utils import timezone

from vng_api_common.constants import Archiefnominatie
from vng_api_common.fields import RSINField, VertrouwelijkheidsAanduidingField
from vng_api_common.models import APIMixin as _APIMixin

from .constants import BetalingsIndicatie
from relativedeltafield import RelativeDeltaField


class DurationField(RelativeDeltaField):
    def formfield(self, form_class=None, **kwargs):
        return super().formfield(form_class=form_class, **kwargs)


class APIMixin(_APIMixin):
    def get_absolute_api_url(self, request=None, **kwargs) -> str:
        kwargs["version"] = "1"
        return super().get_absolute_api_url(request=request, **kwargs)


class Zaak(APIMixin, models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)",
    )

    # CharFields
    omschrijving = models.CharField(
        max_length=80,
        blank=True,
        help_text="Een korte omschrijving van de zaak.",
    )
    toelichting = models.TextField(
        max_length=1000,
        blank=True,
    )

    betalingsindicatie = models.CharField(
        "betalingsindicatie",
        max_length=20,
        blank=True,
        choices=BetalingsIndicatie.choices,
    )
    verlenging_reden = models.CharField(
        "reden verlenging",
        max_length=200,
        blank=True,
    )
    opschorting_reden = models.CharField(
        "reden opschorting",
        max_length=200,
        blank=True,
    )
    opschorting_indicatie = models.BooleanField(
        "indicatie opschorting",
        default=False,
        blank=True,
    )
    opschorting_eerdere_opschorting = models.BooleanField(
        "eerdere opschorting",
        default=False,
        blank=True,
    )

    archiefnominatie = models.CharField(
        "archiefnominatie",
        max_length=40,
        null=True,
        blank=True,
        choices=Archiefnominatie.choices,
        db_index=True,
    )
    archiefstatus = models.CharField(
        "archiefstatus",
        max_length=40,
        null=True,
        db_index=True,
    )
    processobjectaard = models.CharField(
        "procesobjectaard",
        max_length=200,
        blank=True,
    )
    processobject_datumkenmerk = models.CharField(
        "datumkenmerk",
        max_length=250,
        blank=True,
    )
    processobject_identificatie = models.CharField(
        "identificatie",
        max_length=250,
        blank=True,
    )
    processobject_objecttype = models.CharField(
        "objecttype",
        max_length=250,
        blank=True,
    )
    processobject_registratie = models.CharField(
        "registratie",
        max_length=250,
        blank=True,
    )
    communicatiekanaal_naam = models.CharField(
        "communicatiekanaal naam",
        max_length=250,
        blank=True,
    )

    # Date and Datetime Fields
    registratiedatum = models.DateField(
        default=datetime.date.today,
    )
    startdatum = models.DateField(
        db_index=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    einddatum = models.DateField(
        blank=True,
        null=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    einddatum_gepland = models.DateField(
        blank=True,
        null=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    uiterlijke_einddatum_afdoening = models.DateField(
        blank=True,
        null=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    publicatiedatum = models.DateField(
        null=True,
        blank=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    laatste_betaaldatum = models.DateTimeField(
        blank=True,
        null=True,
        default=timezone.now,  # DELETE, only for tests
    )
    archiefactiedatum = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    startdatum_bewaartermijn = models.DateField(
        null=True,
        blank=True,
        default=datetime.date.today,  # DELETE, only for tests
    )
    created_on = models.DateTimeField(
        default=timezone.now,  # DELETE, only for tests
    )

    # Custom Fields
    verantwoordelijke_organisatie = RSINField(default="123456782")
    opdrachtgevende_organisatie = RSINField(default="123456782")

    zaakgeometrie = GeometryField(
        blank=True,
        null=True,
    )

    verlenging_duur = DurationField(
        blank=True,
        null=True,
    )

    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduidingField(default="openbaar")
    selectielijstklasse = models.URLField(blank=True)
    communicatiekanaal = models.URLField(blank=True)
