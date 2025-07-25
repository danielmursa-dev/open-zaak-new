import datetime
import uuid
from typing import List, Optional

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import ArrayField
from django.core import checks, exceptions
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_loose_fk.fields import FkOrURLField
from relativedeltafield import RelativeDeltaField
from vng_api_common.constants import Archiefnominatie
from vng_api_common.descriptors import GegevensGroepType
from vng_api_common.fields import RSINField, VertrouwelijkheidsAanduidingField
from vng_api_common.models import APIMixin as _APIMixin
from zgw_consumers.models import ServiceUrlField

from .constants import BetalingsIndicatie


class GegevensGroepTypeWithReadOnlyFields(GegevensGroepType):
    """
    The GegevensGroepType __set__ method sets fields that were not passed to their default value.
    Zaak.opschorting has the field `eerdere_opschorting` as an internal read only value that should not be changeable.

    This subclass adds read only fields that will be set to their current value when __set__ is called.
    """

    def __init__(self, read_only: tuple = None, **kwargs):
        super().__init__(**kwargs)

        self.read_only = read_only

        read_only_fields_known = set(self.read_only).issubset(set(self.mapping.keys()))
        assert read_only_fields_known, (
            "The fields in 'read_only' must be a subset of the mapping keys"
        )

    def __set__(self, obj, value: Optional[dict]):
        if not value:
            value = {}

        for key in self.read_only:
            value[key] = getattr(obj, self.mapping[key].name)

        super().__set__(obj, value)


class FkOrServiceUrlField(FkOrURLField):
    """
    Support :class:`zgw_consumers.ServiceUrlField` as 'url_field'
    """

    db_default = models.NOT_PROVIDED

    def _add_check_constraint(
        self, options, name="{prefix}{fk_field}_or_{url_base_field}_filled"
    ) -> None:
        """
        Create the DB constraints and add them if they're not present yet.
        """
        if self.null:
            return

        # during migrations, the FK fields are added later, causing the constraint SQL
        # building to blow up. We can ignore this at that time.
        if self.model.__module__ == "__fake__":
            return

        url_base_field = self._url_field.base_field
        # one of both MUST be filled and they cannot be filled both at the
        # same time
        empty_url_base_field = models.Q(**{f"{url_base_field}__isnull": True})
        empty_fk_field = models.Q(**{f"{self.fk_field}__isnull": True})
        fk_filled = ~empty_fk_field & empty_url_base_field
        url_filled = empty_fk_field & ~empty_url_base_field

        constraint = models.CheckConstraint(
            name=name.format(
                prefix=f"{options.app_label}_{options.model_name}_",
                fk_field=self.fk_field,
                url_base_field=url_base_field,
            ),
            check=fk_filled | url_filled,
        )
        options.constraints.append(constraint)
        # ensure this can be picked up by migrations by making it "explicitly defined"
        if "constraints" not in options.original_attrs:
            options.original_attrs["constraints"] = options.constraints
        return

    def check(self, **kwargs) -> List[checks.Error]:
        errors = []
        if not isinstance(self._fk_field, models.ForeignKey):
            errors.append(
                checks.Error(
                    "The field passed to 'fk_field' should be a ForeignKey",
                    obj=self,
                    id="fk_or_url_field.E001",
                )
            )

        if not isinstance(self._url_field, ServiceUrlField):
            errors.append(
                checks.Error(
                    "The field passed to 'url_field' should be a ServiceUrlField",
                    obj=self,
                    id="open_zaak.E001",
                )
            )

        return errors


def validate_relative_url(value):
    message = _("Enter a valid relative URL.")

    if value.startswith(("https://", "http://", "fps://", "ftps://", "/")):
        raise exceptions.ValidationError(
            message, code="invalid", params={"value": value}
        )


class RelativeURLField(models.CharField):
    """
    Model field for relative urls with build-in regex validator
    """

    default_validators = [validate_relative_url]

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs.setdefault("max_length", 1000)
        super().__init__(verbose_name, name, **kwargs)


class ServiceFkField(models.ForeignKey):
    """
    FK to Service model field
    """

    def __init__(self, **kwargs):
        kwargs["to"] = "zgw_consumers.Service"
        kwargs.setdefault("on_delete", models.PROTECT)
        kwargs.setdefault("related_name", "+")  # no reverse relations by default
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)

        super().__init__(**kwargs)


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

    producten_of_diensten = ArrayField(
        models.URLField(max_length=1000),
        default=list,
        blank=True,
    )

    # Descriptors
    processobject = GegevensGroepType(
        {
            "datumkenmerk": processobject_datumkenmerk,
            "identificatie": processobject_identificatie,
            "objecttype": processobject_objecttype,
            "registratie": processobject_registratie,
        },
    )

    opschorting = GegevensGroepTypeWithReadOnlyFields(
        mapping={
            "indicatie": opschorting_indicatie,
            "eerdere_opschorting": opschorting_eerdere_opschorting,
            "reden": opschorting_reden,
        },
        read_only=("eerdere_opschorting",),
    )

    verlenging = GegevensGroepType({"reden": verlenging_reden, "duur": verlenging_duur})

    # FK relations

    hoofdzaak = models.ForeignKey(
        "self",
        limit_choices_to={"hoofdzaak__isnull": True},
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="deelzaken",
        verbose_name="is deelzaak van",
    )

    # ZaakType

    _zaaktype_base_url = ServiceFkField(
        help_text="Basis deel van URL-referentie naar het extern ZAAKTYPE (in een andere Catalogi API).",
    )
    _zaaktype_relative_url = RelativeURLField(
        "zaaktype relative url",
        blank=True,
        null=True,
        help_text="Relatief deel van URL-referentie naar het extern ZAAKTYPE (in een andere Catalogi API).",
    )
    _zaaktype_url = ServiceUrlField(
        base_field="_zaaktype_base_url",
        relative_field="_zaaktype_relative_url",
        verbose_name="extern zaaktype",
        null=True,
        blank=True,
        max_length=1000,
        help_text=_(
            "URL-referentie naar extern ZAAKTYPE (in een andere Catalogi API)."
        ),
    )
    _zaaktype = models.ForeignKey(
        "catalogi.ZaakType",
        on_delete=models.PROTECT,
        help_text="URL-referentie naar het ZAAKTYPE (in de Catalogi API).",
        null=True,
        blank=True,
    )
    zaaktype = FkOrServiceUrlField(
        fk_field="_zaaktype",
        url_field="_zaaktype_url",
        help_text="URL-referentie naar het ZAAKTYPE (in de Catalogi API).",
        null=True,
    )

    # Zaak ID

    identificatie = models.CharField(
        blank=True,
        max_length=40,
        default="",
        db_index=True,
    )
    bronorganisatie = RSINField(default="")
